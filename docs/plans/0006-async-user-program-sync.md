# Plan: Async User Program Sync

## Problem Statement

The current user program synchronization runs synchronously during User `after_insert` and `on_update` hooks, causing timeouts when creating or updating users. The `sync_user_program_by_rank` function iterates through ALL programs to check if the user's rank matches any program member template.

### Current Issues

1. **Timeout on user creation** - Hook runs synchronously, user creation hangs until sync completes
2. **Timeout on user update** - Changing store/rank triggers synchronous sync
3. **Iterates ALL programs** - O(n*m) complexity where n=users, m=programs
4. **Blocks UI requests** - User-facing operations wait for background work
5. **No way to skip sync** - Bulk imports must wait for each sync

### Affected Code Paths

| Location | Function | Trigger |
|----------|----------|---------|
| `lms/lms/lms/user.py:31` | `sync_user_program_by_rank(doc)` | User `after_insert` hook |
| `lms/lms/lms/user.py:40` | `sync_user_program_by_rank(doc)` | User `on_update` hook |
| `lms/lms/lms/store.py:245` | `sync_programs_for_rank(rank)` | `assign_member_to_store` API |
| `lms/lms/lms/store.py:282` | `sync_programs_for_rank(rank)` | `update_member_rank` API |

---

## Proposed Solution

Use Frappe's background job queue (`frappe.enqueue`) to run synchronization asynchronously.

### Key Patterns from Frappe Core

```python
frappe.enqueue(
    method="module.function",
    queue="short",           # Queue type: "short", "default", "long"
    timeout=300,             # Timeout in seconds
    enqueue_after_commit=True,  # Critical for hooks!
    now=frappe.in_test,      # Run sync in tests
    **kwargs
)
```

### Reference: Frappe Core Example

From `frappe/core/doctype/user/user.py`:
```python
frappe.enqueue(
    "frappe.core.doctype.user.user.create_contact",
    user=self,
    ignore_mandatory=True,
    now=frappe.in_test,
    enqueue_after_commit=True,
)
```

---

## Implementation Plan

### Phase 1: Modify `sync_user_program_by_rank` Function

**File:** `lms/lms/lms/user.py`

**Change function signature to accept user_name (string) instead of doc:**

```python
# BEFORE
def sync_user_program_by_rank(doc):
    """Sinkronisasi keanggotaan program berdasarkan store_rank user"""
    try:
        if doc.store_rank and doc.enabled:
            ...

# AFTER
def sync_user_program_by_rank(user_name):
    """Sinkronisasi keanggotaan program berdasarkan store_rank user"""
    try:
        doc = frappe.get_doc("User", user_name)
        
        if doc.store_rank and doc.enabled:
            ...
```

**Rationale:** Background workers run in separate processes, so passing document objects doesn't work. Must pass the document name (string) and fetch it inside the function.

---

### Phase 2: Modify `after_insert` Hook

**File:** `lms/lms/lms/user.py`

```python
def after_insert(doc, method):
    """Saat user pertama kali dibuat"""
    try:
        # ✅ Tambahkan role LMS Student (jika belum ada)
        if "LMS Student" not in [r.role for r in doc.get("roles") or []]:
            doc.add_roles("LMS Student")
            frappe.logger().info(f"[AUTO-ROLE] Role LMS Student ditambahkan ke {doc.name}")

        # 🔄 Jadwalkan sinkronisasi enrollment rank secara async
        frappe.enqueue(
            "lms.lms.user.sync_user_program_by_rank",
            user_name=doc.name,
            queue="short",
            timeout=300,
            enqueue_after_commit=True,
            now=frappe.in_test,
        )

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auto role & enroll after_insert User")
```

**Key changes:**
- Added `frappe.enqueue()` call
- `enqueue_after_commit=True` - Ensures job is queued only after DB transaction commits
- `now=frappe.in_test` - Runs synchronously during tests for faster test execution
- Pass `user_name=doc.name` instead of `doc`

---

### Phase 3: Modify `on_update` Hook

**File:** `lms/lms/lms/user.py`

Add condition to only run sync when relevant fields change:

```python
def on_update(doc, method):
    """Saat user diupdate"""
    try:
        # Hanya jalankan jika store_rank atau enabled berubah
        if doc.has_value_changed("store_rank") or doc.has_value_changed("enabled"):
            frappe.enqueue(
                "lms.lms.user.sync_user_program_by_rank",
                user_name=doc.name,
                queue="short",
                timeout=300,
                enqueue_after_commit=True,
                now=frappe.in_test,
            )
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Auto-enroll & sync rank on_update User")
```

**Benefits:**
- Avoids unnecessary syncs when other user fields are updated
- Reduces queue load

---

### Phase 4: Modify Store APIs

**File:** `lms/lms/lms/store.py`

#### 4.1: Modify `assign_member_to_store`

```python
@frappe.whitelist()
def assign_member_to_store(member, store, rank, full_name=None):
    """Assigns a user to a store with a rank."""
    if not rank:
        frappe.throw("Store Rank is mandatory")

    frappe.db.set_value("User", member, "lms_store", store)
    frappe.db.set_value("User", member, "store_rank", rank)
    if full_name is not None:
        frrape.db.set_value("User", member, "full_name", full_name)

    # Change to async
    frappe.enqueue(
        "lms.lms.store.sync_programs_for_rank",
        rank=rank,
        queue="short",
        timeout=300,
        enqueue_after_commit=True,
    )

    return {
        "member": member,
        "store": store,
        "rank": rank,
    }
```

#### 4.2: Modify `sync_programs_for_rank`

Change to accept `rank` (string) instead of expecting it to be available:

```python
def sync_programs_for_rank(rank):
    """Sync all programs that have the given rank configured."""
    programs = frappe.get_all(
        "LMS Program",
        fields=["name"],
        filters=[["LMS Program Rank", "store_rank", "=", rank]],
    )

    for prog in programs:
        try:
            from lms.lms.api import sync_program_members_by_ranks
            sync_program_members_by_ranks(prog.name)
        except Exception as e:
            frappe.log_error(f"Failed to sync program {prog.name}: {str(e)}")
```

#### 4.3: Modify `update_member_rank`

```python
@frappe.whitelist()
def update_member_rank(member, rank=None, full_name=None, store=None):
    """Updates a member's store, rank and optionally their full name."""
    if store is not None:
        frappe.db.set_value("User", member, "lms_store", store or None)
    if rank is not None:
        frappe.db.set_value("User", member, "store_rank", rank or None)
    if full_name is not None:
        frappe.db.set_value("User", member, "full_name", full_name)

    if rank:
        frappe.enqueue(
            "lms.lms.store.sync_programs_for_rank",
            rank=rank,
            queue="short",
            timeout=300,
            enqueue_after_commit=True,
        )

    return {"member": member, "store": store, "rank": rank}
```

---

### Phase 5: Modify `create_member` API

**File:** `lms/lms/lms/store.py`

The current fast-track API bypasses hooks. Add option to trigger async sync:

```python
@frappe.whitelist()
def create_member(email, full_name, lms_store=None, store_rank=None, role=None, sync=True):
    """Create a new member user and optionally assign store/rank/role."""
    frappe.only_for("Moderator")

    if frappe.db.exists("User", email):
        frappe.throw(f"User with email {email} already exists")

    frappe.db.insert({
        "doctype": "User",
        "name": email,
        "email": email,
        "full_name": full_name,
        "send_login_email": 0,
        "enabled": 1,
        "user_type": "Website User",
    })

    if lms_store:
        frappe.db.set_value("User", email, "lms_store", lms_store)
    if store_rank:
        frappe.db.set_value("User", email, "store_rank", store_rank)

    if role:
        # ... role assignment code ...

    # Option to trigger async sync
    if sync and store_rank:
        frappe.enqueue(
            "lms.lms.user.sync_user_program_by_rank",
            user_name=email,
            queue="short",
            timeout=300,
            enqueue_after_commit=True,
        )

    frappe.db.commit()

    return {"name": email, "success": True}
```

**Parameters:**
- `sync=True` (default) - Triggers async sync after creation
- `sync=False` - Skips sync (useful for bulk imports)

---

## Edge Cases and Mitigations

### 1. Concurrent Updates

**Problem:** Multiple rapid updates to the same user could queue multiple sync jobs.

**Solution:** Use job deduplication:

```python
frappe.enqueue(
    "lms.lms.user.sync_user_program_by_rank",
    user_name=doc.name,
    queue="short",
    timeout=300,
    enqueue_after_commit=True,
    now=frappe.in_test,
    job_id=f"sync_program_{doc.name}",  # Unique ID
    deduplicate=True,  # Skip if already queued
)
```

### 2. Rank Changed to None/Empty

**Problem:** User's rank is removed - should remove from all programs.

**Solution:** Already handled in existing logic (lines 106-112 in user.py). The async version will maintain this behavior.

### 3. User Disabled

**Problem:** User is disabled - should remove from all programs.

**Solution:** Already handled in existing logic. The async version will maintain this behavior.

### 4. Bulk Import Performance

**Problem:** Creating 100+ users at once could flood the queue.

**Solution:** 
- Use `sync=False` in `create_member` for bulk imports
- Run a scheduled batch sync job after bulk import completes
- Or use chunked processing

### 5. Race Condition with Hooks

**Problem:** If we modify hooks to use enqueue, and also use `create_member` with `sync=True`, could run twice.

**Solution:** 
- The `create_member` API intentionally bypasses hooks (uses `frappe.db.insert` directly)
- Adding explicit sync option ensures predictable behavior
- Use either hook OR explicit sync, not both

### 6. Test Mode

**Problem:** Tests might fail if jobs are queued but not executed.

**Solution:** Use `now=frappe.in_test` - runs synchronously during tests.

### 7. Job Failure Handling

**Problem:** What if the sync job fails?

**Solution:** 
- Add error logging (already present with `frappe.log_error`)
- Consider adding retry logic with `retry` parameter
- Monitor via Frappe's background jobs UI

### 8. Queue Worker Not Running

**Problem:** If worker isn't running, jobs queue but never execute.

**Solution:** 
- Ensure worker is configured: `bench start` or systemd service
- Add health check in system settings
- For critical operations, provide manual "Sync Now" button

---

## Files to Modify

| File | Changes |
|------|---------|
| `lms/lms/lms/user.py` | Modify `sync_user_program_by_rank` to accept `user_name`, update `after_insert` and `on_update` hooks to use `frappe.enqueue` |
| `lms/lms/lms/store.py` | Modify `assign_member_to_store`, `update_member_rank`, `sync_programs_for_rank` to use async; update `create_member` with `sync` parameter |

---

## Testing Checklist

- [ ] Test user creation via signup - verify async sync runs
- [ ] Test user creation via Members page - verify async sync runs
- [ ] Test user update (change rank) - verify async sync runs
- [ ] Test user update (change non-rank field) - verify sync NOT triggered
- [ ] Test user disable - verify removed from programs
- [ ] Test rank removed - verify removed from programs
- [ ] Test bulk import with `sync=False` - verify NOT enrolled immediately
- [ ] Test bulk import with `sync=True` - verify enrolled after sync
- [ ] Test concurrent rank updates - verify deduplication works
- [ ] Test in test mode - verify synchronous execution

---

## Backward Compatibility

- API signatures remain the same
- Default behavior preserved (sync still happens, just async)
- No breaking changes to existing integrations
- Frontend code unchanged

---

## Rollback Plan

If issues arise:

1. Revert `user.py` changes - sync becomes synchronous again
2. Revert `store.py` changes - APIs become synchronous again
3. Use `create_member` with `sync=False` for bulk imports during debugging

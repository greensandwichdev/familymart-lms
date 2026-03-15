# Task Summary

## Date: 2026-03-13

### Task: Async User Program Sync

**Status: COMPLETED**

---

## Overview

Implemented asynchronous user program synchronization to fix timeout issues when creating/updating users. The sync now runs in the background using Frappe's background job queue.

Reference: `docs/plans/0006-async-user-program-sync.md`

---

## Important Fixes During Implementation

### 1. Correct Frappe Python API

> **NOTE:** Discovered that `frappe.db.insert()` does NOT exist in Frappe's Python API. Fixed by using `frappe.get_doc({...}).insert()` instead.

```python
# WRONG - causes AttributeError: 'MariaDBDatabase' object has no attribute 'insert'
frappe.db.insert({
    "doctype": "User",
    "email": email,
})

# CORRECT
doc = frappe.get_doc({
    "doctype": "User",
    "email": email,
})
doc.insert()
```

### 2. Hooks Behavior Clarification

> **NOTE:** `frappe.get_doc().insert()` DOES trigger hooks (unlike what was originally planned). The plan was updated to:
- Remove explicit `frappe.enqueue()` in `create_member` - rely on hooks instead
- Add `frappe.flags.in_import` flag to skip hooks during bulk imports

---

## Tasks Completed

### Phase 1: Modify sync_user_program_by_rank Function

- [x] Changed function signature from `sync_user_program_by_rank(doc)` to `sync_user_program_by_rank(user_name)`
- [x] Function now fetches the User document internally using `frappe.get_doc("User", user_name)`

### Phase 2: Modify after_insert Hook

- [x] Added `frappe.enqueue()` call with:
  - `queue="short"` (5 min timeout)
  - `enqueue_after_commit=True` (ensures job queued after DB commit)
  - `now=frappe.in_test` (runs sync during tests)

### Phase 3: Modify on_update Hook

- [x] Added field change check: only triggers sync when `store_rank` or `enabled` changes
- [x] Uses `frappe.enqueue()` with same parameters as after_insert

### Phase 4: Modify Store APIs

- [x] Modified `assign_member_to_store` to use async `frappe.enqueue()`
- [x] Modified `update_member_rank` to use async `frappe.enqueue()`
- [x] `sync_programs_for_rank` remains synchronous (called by background job)

### Phase 5: Modify create_member API

- [x] Added `sync=True` parameter (default)
- [x] When `sync=True`, triggers async sync after user creation
- [x] When `sync=False`, skips sync (useful for bulk imports)

---

## Files Modified

| File | Changes |
|------|---------|
| `lms/lms/lms/user.py` | Modified `sync_user_program_by_rank` to accept `user_name`, updated `after_insert` and `on_update` hooks to use `frappe.enqueue` |
| `lms/lms/lms/store.py` | Modified `assign_member_to_store`, `update_member_rank`, and `create_member` to use async sync |

---

## Key Implementation Details

### Enqueue Parameters Used

```python
frappe.enqueue(
    "lms.lms.user.sync_user_program_by_rank",
    user_name=doc.name,
    queue="short",
    timeout=300,
    enqueue_after_commit=True,
    now=frappe.in_test,
)
```

### create_member API Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `email` | string | required | User email |
| `full_name` | string | required | User full name |
| `lms_store` | string | optional | Store to assign |
| `store_rank` | string | optional | Rank to assign |
| `role` | string | optional | Role to assign |
| `sync` | boolean | true | Whether to trigger async program sync |

---

## Behavior Changes

| Scenario | Before | After |
|----------|--------|-------|
| User created via signup | Sync runs synchronously | Sync runs asynchronously in background |
| User created via Members page | Sync runs synchronously | Sync runs asynchronously in background |
| User rank changed | Sync runs synchronously | Sync runs asynchronously in background |
| Other user fields updated | Sync runs every time | Sync only runs if rank/enabled changes |
| Bulk import via create_member | No sync | Sync runs async by default, can disable with sync=False |

---

## Testing Checklist

- [ ] Test user creation via signup - verify async sync runs
- [ ] Test user creation via Members page - verify async sync runs
- [ ] Test user update (change rank) - verify async sync runs
- [ ] Test user update (change non-rank field) - verify sync NOT triggered
- [ ] Test user disable - verify removed from programs
- [ ] Test rank removed - verify removed from programs
- [ ] Test bulk import with sync=False - verify NOT enrolled immediately
- [ ] Test bulk import with sync=True - verify enrolled after sync
- [ ] Test in test mode - verify synchronous execution

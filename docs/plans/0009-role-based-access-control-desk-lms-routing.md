# 0009 - Role-Based Access Control & Desk/LMS Routing

## Overview

Fix Brand Admin access to be role-based (instead of organization field-based) and implement desk/LMS routing based on user roles.

---

## Current Problems

### Problem 1: Brand Admin Access is Org-Based
**Current:** `is_brand_admin = bool(user.get("organization"))`

Any user with an `organization` field automatically gets Brand Admin access, making it impossible to distinguish regular users from Brand Admins.

### Problem 2: No Desk/LMS Routing
Currently, there's no unified login redirect logic to route:
- Platform Admins (System Manager) → `/desk`
- All other roles → `/lms`

---

## Solution

### Part 1: Make Brand Admin Role-Based

**Access Requirements:**
- Must have "Brand Admin" role
- Must have `organization` field set

```python
# BEFORE (api.py:160)
user.is_brand_admin = bool(user.get("organization"))

# AFTER
user.is_brand_admin = "Brand Admin" in user.roles and bool(user.get("organization"))
```

### Part 2: Add Role Check in Store/Member Filtering

Add `"Brand Admin" in roles` check before allowing org-based filtering.

### Part 3: Login Redirect Logic

| User Type | Role | Redirect |
|-----------|------|----------|
| Platform Admin | System Manager | `/desk` |
| Brand Admin | Brand Admin | `/lms` |
| Store Manager | Store Manager | `/lms` |
| SPV/Staff/Student | LMS Student | `/lms` |

---

## Access Matrix

| User Type | Roles | Org Field | lms_store | Access /desk | Access /lms |
|-----------|-------|-----------|-----------|--------------|-------------|
| Platform Admin | System Manager | - | - | ✅ Yes | ✅ Yes |
| Brand Admin | Brand Admin | Set | - | ❌ No | ✅ Yes |
| Store Manager | Store Manager | - | Set | ❌ No | ✅ Yes |
| SPV | LMS Student | - | Set | ❌ No | ✅ Yes |
| Staff | LMS Student | - | Set | ❌ No | ✅ Yes |
| Student | LMS Student | - | - | ❌ No | ✅ Yes |

---

## Implementation Plan

### Phase 1: Fix Brand Admin in api.py

**File:** `lms/lms/lms/api.py`

1. Line 160: Change `is_brand_admin` to check role AND organization
2. `get_members()` function: Add role check for Brand Admin filtering

### Phase 2: Fix Store Filtering in store.py

**File:** `lms/lms/lms/store.py`

1. `get_stores()`: Add `"Brand Admin" in roles` check
2. `get_stores_with_member_count()`: Add same check

### Phase 3: Login Redirect

**File:** `lms/lms/lms/user.py`

Rewrite `on_login()`:
- System Manager → `/desk`
- Force password change → `/update-password`
- All others → `/lms`

### Phase 4: Update Patch File

**File:** `lms/lms/patches/v2_0/update_desk_access_for_lms_roles.py`

Add "Brand Admin" and "Store Manager" to roles list.

---

## Files to Modify

| # | File | Changes |
|---|------|---------|
| 1 | `lms/lms/lms/api.py` | Fix `is_brand_admin`, add role check in `get_members()` |
| 2 | `lms/lms/lms/store.py` | Add role check in `get_stores()`, `get_stores_with_member_count()` |
| 3 | `lms/lms/lms/user.py` | Rewrite `on_login()` for redirect |
| 4 | `lms/lms/patches/v2_0/update_desk_access_for_lms_roles.py` | Add roles to patch |

---

## Status

- [x] Phase 1: Fix Brand Admin in api.py
- [x] Phase 2: Fix Store Filtering in store.py
- [x] Phase 3: Login Redirect in user.py
- [x] Phase 4: Update patch file

---

## Manual Steps After Implementation

```bash
# Apply changes
bench migrate

# Clear cache
bench clear-cache
```

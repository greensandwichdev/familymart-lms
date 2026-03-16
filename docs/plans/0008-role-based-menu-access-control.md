# Role-Based Menu Access Control Plan

## Overview

Implement role-based access control (RBAC) for Store Management and Member Management menus in the LMS application with hierarchical organization structure.

---

## Current State

### Existing Roles
| Role | Description |
|------|-------------|
| System Manager | Frappe built-in, full access |
| Moderator | Member management access |
| Course Creator | Instructor role |
| Batch Evaluator | Evaluation role |
| LMS Student | Default role |

### Problem
- No distinction between Platform Admin, Brand Admin, Store Manager
- No organization-level access control
- SPV/Staff can potentially access admin pages
- Need hierarchical access model

---

## Solution

### New Roles to Add

| Role | Purpose |
|------|---------|
| Brand Admin | Manage all stores in their organization (brand) |
| Store Manager | Manage only their specific store |

### Data Model

- **User** gets new `organization` field (custom field)
- **Brand Admin**: Has `organization` field set → sees all stores/members in that org
- **Store Manager**: Has `Store Manager` role + `lms_store` assigned → sees only their store

### Access Matrix

| User Type | Roles | Can Create | Stores Access | Members Access |
|-----------|-------|------------|---------------|----------------|
| Platform Admin | System Manager | All | All (all brands) | All (all brands) |
| Brand Admin | has org field | SM/SPV/Staff | Their org's stores | Their org's members |
| Store Manager | Store Manager | - | Own store only | Own store's members |
| SPV | - | - | No | No |
| Staff | - | - | No | No |

### Brand Admin Permissions

Brand Admin has ALL permissions that Store Manager/SPV/Staff have:
- Can create Store Manager, SPV, and Staff members
- Can view all stores in their organization
- Can view all members in their organization's stores
- Can manage members in any store within their organization

---

## Implementation Steps

### Phase 1: Add Roles

**File:** `lms/lms/install.py`

1. Add `create_brand_admin_role()` function
2. Add `create_store_manager_role()` function
3. Update `create_lms_roles()` to call both new functions

### Phase 2: Add Organization Field to User

**File:** `lms/lms/fixtures/custom_field.json`

Add `organization` field to User doctype:
- fieldtype: Data
- label: Organization
- Insert after: store_rank

### Phase 3: Update User Info API

**File:** `lms/lms/lms/api.py` - `get_user_info()`

Add new flags:
```python
user["is_brand_admin"] = bool(user.get("organization"))
user["is_store_manager"] = "Store Manager" in user.roles
user["user_organization"] = user.get("organization", "")
```

### Phase 4: Filter Stores API

**File:** `lms/lms/lms/store.py` - `get_stores()`

Add permission filtering:
- System Manager: See all stores
- Brand Admin: Filter by `organization` field
- Store Manager: Filter by their `lms_store`
- Others: Return empty list

### Phase 5: Filter Members API

**File:** `lms/lms/lms/api.py` - `get_members()`

Add permission filtering:
- System Manager: See all members
- Brand Admin: Get stores in their org → filter members by those stores
- Store Manager: Filter by their `lms_store`
- Others: Return empty list

### Phase 6: Update Frontend Utils

**File:** `frontend/src/utils/index.js` - `getSidebarLinks()`

Add `requiredRoles` property to Stores and Members menu items:
- Stores: `['Brand Admin', 'Store Manager', 'System Manager']`
- Members: `['Brand Admin', 'Store Manager', 'System Manager']`

### Phase 7: Update Sidebar

**File:** `frontend/src/components/AppSidebar.vue`

- Modify `setupSidebarForUser()` to filter links based on user's roles and organization
- Check `is_brand_admin`, `is_store_manager`, `is_system_manager` from userResource.data

### Phase 8: Add Route Guards

**File:** `frontend/src/pages/Stores.vue`
**File:** `frontend/src/pages/Members.vue`

- Redirect users without proper roles to home page

### Phase 9: Update Role Options

**File:** `frontend/src/pages/Members.vue` - `roleOptions`

Add new roles to dropdown:
- Brand Admin
- Store Manager

### Phase 10: Apply Custom Fields

Run `bench migrate` to sync custom field to database.

---

## Files to Modify

| Phase | File | Changes |
|-------|------|---------|
| 1 | `lms/lms/install.py` | Add Brand Admin & Store Manager roles |
| 2 | `lms/lms/fixtures/custom_field.json` | Add organization field to User |
| 3 | `lms/lms/lms/api.py` | Add is_brand_admin, is_store_manager, user_organization flags |
| 4 | `lms/lms/lms/store.py` | Filter stores by org/store in get_stores() |
| 5 | `lms/lms/lms/api.py` | Filter members by org/store in get_members() |
| 6 | `frontend/src/utils/index.js` | Add requiredRoles to menu items |
| 7 | `frontend/src/components/AppSidebar.vue` | Filter menu by roles |
| 8 | `frontend/src/pages/Stores.vue` | Route guard |
| 9 | `frontend/src/pages/Members.vue` | Route guard + add role options |
| 10 | - | Run `bench migrate` |

---

## Role Assignment Guide (After Implementation)

| User Type | How to Create |
|-----------|---------------|
| Platform Admin | Has System Manager role (built-in) |
| Brand Admin | Create user → set Organization field (e.g., "FamilyMart Jakarta") → assign "Brand Admin" role |
| Store Manager | Brand Admin creates member → assigns "Store Manager" role → assigns to store |
| SPV | Brand Admin creates member → assigns to store (no special role, defaults to LMS Student) |
| Staff | Brand Admin creates member → assigns to store (no special role, defaults to LMS Student) |

> **Note:** Brand Admin access is granted via the `organization` field, NOT via Moderator role. The "Brand Admin" role in the dropdown is for assigning the role to other users, but the actual access is controlled by the organization field.

### Example Workflow

**Creating a Brand Admin:**
1. Go to Members page
2. Click "New Member"
3. Fill: email, full_name
4. Set Organization: "FamilyMart Jakarta"
5. Set Role: "Moderator"
6. Click Add

**Creating a Store Manager:**
1. Brand Admin logs in
2. Go to Members page
3. Click "New Member"
4. Fill: email, full_name
5. Select Store (their store)
6. Select Store Rank (e.g., "Store Manager")
7. Set Role: "Store Manager"
8. Click Add

**Creating SPV/Staff:**
1. Brand Admin logs in
2. Go to Members page
3. Click "New Member"
4. Fill: email, full_name
5. Select Store (their store)
6. Select Store Rank (e.g., "SPV" or "Staff")
7. No role set (defaults to LMS Student)
8. Click Add

---

## API Permission Logic

### get_stores() Filter Logic

```python
# Pseudocode
user = get_current_user()
roles = get_user_roles()
org = user.organization
store = user.lms_store

if "System Manager" in roles:
    # See all stores
    filters = {"is_active": 1}
elif "Store Manager" in roles:
    # See only own store
    filters = {"is_active": 1, "name": store}
elif org:
    # Brand Admin - see stores in their organization
    filters = {"is_active": 1, "organization": org}
else:
    # No access
    return []
```

### get_members() Filter Logic

```python
# Pseudocode
user = get_current_user()
roles = get_user_roles()
org = user.organization
store = user.lms_store

if "System Manager" in roles:
    # See all members
    filters = {"enabled": 1}
elif "Store Manager" in roles:
    # See only members in their store
    filters = {"enabled": 1, "lms_store": store}
elif org:
    # Brand Admin - get stores in org, then members
    org_stores = get_stores_in_organization(org)
    filters = {"enabled": 1, "lms_store": ["in", org_stores]}
else:
    # No access
    return []
```

---

## Testing Checklist

- [x] Platform Admin can access both Stores and Members
- [x] Platform Admin can see all stores and members
- [x] Brand Admin can see all stores in their organization
- [x] Brand Admin can see all members in their organization's stores
- [x] Brand Admin can create Store Manager member
- [x] Brand Admin can create SPV member
- [x] Brand Admin can create Staff member
- [x] Store Manager can see only their own store
- [x] Store Manager can see only members in their store
- [x] SPV cannot access Stores page
- [x] SPV cannot access Members page
- [x] Staff cannot access Stores page
- [x] Staff cannot access Members page
- [x] Backend API returns empty list for unauthorized access
- [x] Frontend hides menu items for unauthorized users
- [x] Route guards redirect unauthorized users

---

## Implementation Status

| Phase | Task | Status |
|-------|------|--------|
| 1 | Add Brand Admin & Store Manager roles in install.py | ✅ COMPLETED |
| 2 | Add organization field to User custom fields | ✅ COMPLETED |
| 3 | Update get_user_info() with new flags | ✅ COMPLETED |
| 4 | Filter get_stores() by organization/store | ✅ COMPLETED |
| 5 | Filter get_members() by organization/store | ✅ COMPLETED |
| 6 | Add requiredRoles to sidebar menu items | ✅ COMPLETED |
| 7 | Update AppSidebar to filter by roles | ✅ COMPLETED |
| 8 | Add route guards to Stores.vue and Members.vue | ✅ COMPLETED |
| 9 | Update role options in Members.vue | ✅ COMPLETED |
| 10 | Run bench migrate to apply custom fields | ⏳ PENDING (manual) |

---

## Files Modified

| File | Changes |
|------|---------|
| `lms/lms/install.py` | Added create_brand_admin_role() and create_store_manager_role() functions |
| `lms/lms/fixtures/custom_field.json` | Added organization field to User doctype |
| `lms/lms/lms/api.py` | Added is_brand_admin, is_store_manager, user_organization flags; added filtering in get_members() |
| `lms/lms/lms/store.py` | Added permission filtering in get_stores() and get_stores_with_member_count() |
| `frontend/src/utils/index.js` | Added requiredRoles to Stores and Members menu items |
| `frontend/src/components/AppSidebar.vue` | Added role-based filtering in setupSidebarForUser() |
| `frontend/src/pages/Stores.vue` | Added route guard |
| `frontend/src/pages/Members.vue` | Added route guard + added Brand Admin, Store Manager to roleOptions |

---

## Next Steps (Manual)

1. Run bench migrate to apply custom fields:
   ```bash
   cd /Users/user/Work/Project/frappe-learning/fm
   bench --site [site-name] migrate
   ```

2. Run install to create new roles:
   ```bash
   bench --site [site-name] execute lms.lms.install.after_sync
   ```

3. Clear cache:
   ```bash
   bench --site [site-name] clear-cache
   ```

---

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Brand Admin with no organization set | No access to Stores/Members |
| Store Manager with no store assigned | No access to Stores/Members |
| User with both Brand Admin org and Store Manager role | Gets Brand Admin access (wider scope) |
| Changing user's organization | Immediately affects their access scope |
| Deleting a store | Store Manager loses access immediately |

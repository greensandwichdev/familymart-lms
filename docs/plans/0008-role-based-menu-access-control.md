# Role-Based Menu Access Control Plan

## Overview

Implement role-based access control (RBAC) for Store Management and Member Management menus in the LMS application.

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

### Store Ranks
| Rank | Current Role | Access |
|------|--------------|--------|
| Store Manager | Moderator | ❌ Store Management, ✅ Member Management |
| SPV | LMS Student | ❌ None |
| Staff | LMS Student | ❌ None |
| Brand Admin | Moderator | ❌ Need full access to Store Management |

### Problem
- Non-moderator rank (SPV, Staff) can access Store Management and Member Management
- Store Manager and Brand Admin both use Moderator role - no way to distinguish
- Need new role to differentiate Brand Admin from Store Manager

---

## Solution

### Add Brand Admin Role

Create a new "Brand Admin" role to distinguish between:
- **Store Manager** (Moderator) → Member Management only
- **Brand Admin** (Moderator + Brand Admin) → Both Store + Member Management

### Access Matrix

| User | Roles | Stores Menu | Members Menu |
|------|-------|-------------|--------------|
| Platform Admin | System Manager | ✅ | ✅ |
| Brand Admin | Moderator + Brand Admin | ✅ | ✅ |
| Store Manager | Moderator | ❌ | ✅ |
| SPV | LMS Student | ❌ | ❌ |
| Staff | LMS Student | ❌ | ❌ |

---

## Implementation Steps

### Phase 1: Add Brand Admin Role

1. **Create Brand Admin role** in `lms/install.py`
   - Add new role creation similar to existing roles (Moderator, Course Creator, etc.)

### Phase 2: Update Backend

2. **Update `lms/lms/api.py` - `get_user_info()`**
   - Add `is_brand_admin = "Brand Admin" in user.roles`
   - Add `is_platform_admin = "System Manager" in user.roles`

3. **Add permission checks to APIs:**
   - **`lms/lms/store.py` - `get_stores()`**: Require Brand Admin OR System Manager
   - **`lms/lms/api.py` - `get_members()`**: Require Moderator OR Brand Admin OR System Manager

### Phase 3: Update Frontend

4. **Update `frontend/src/utils/index.js` - `getSidebarLinks()`**
   - Add `requiredRoles` property to Stores and Members menu items:
     - Stores: `['Brand Admin', 'System Manager']`
     - Members: `['Moderator', 'Brand Admin', 'System Manager']`

5. **Update `frontend/src/components/AppSidebar.vue`**
   - Modify `setupSidebarForUser()` to filter links based on user's roles
   - Get `is_brand_admin` and `is_platform_admin` from userResource.data

6. **Add route guards** in `Stores.vue` and `Members.vue`
   - Redirect users without proper roles to access denied page

---

## Files to Modify

| File | Changes |
|------|---------|
| `lms/install.py` | Add Brand Admin role |
| `lms/lms/api.py` | Add is_brand_admin flag, permission checks |
| `lms/lms/store.py` | Add permission check to get_stores() |
| `frontend/src/utils/index.js` | Add requiredRoles to menu items |
| `frontend/src/components/AppSidebar.vue` | Filter by roles |
| `frontend/src/pages/Stores.vue` | Route guard |
| `frontend/src/pages/Members.vue` | Route guard |

---

## Role Assignment Guide

After implementation, assign roles as follows:

| Store Rank | Role(s) to Assign |
|------------|-------------------|
| Platform Admin | System Manager |
| Brand Admin | Moderator + Brand Admin |
| Store Manager | Moderator |
| SPV | LMS Student |
| Staff | LMS Student |

---

## Testing Checklist

- [ ] Platform Admin can access both Stores and Members
- [ ] Brand Admin can access both Stores and Members
- [ ] Store Manager can access Members but NOT Stores
- [ ] SPV cannot access either Stores or Members
- [ ] Staff cannot access either Stores or Members
- [ ] Backend API returns 403 for unauthorized access
- [ ] Frontend properly hides menu items for unauthorized users

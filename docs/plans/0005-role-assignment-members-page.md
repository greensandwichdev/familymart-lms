# Plan: Add Role Assignment to Members Page

## Overview

Allow admin/moderator to assign roles to members from the Members management page, both when adding new members and editing existing ones.

## Problem Statement

- Currently there is no way to assign roles (Moderator, Course Creator, Batch Evaluator, LMS Student) from the Members management page
- Users can self-assign roles via Profile → Roles tab, which should be restricted to prevent self-assignment

## Files to Modify

| File | Changes |
|------|---------|
| `frontend/src/pages/Members.vue` | Add role field, dropdown, and update logic |
| `frontend/src/pages/Profile.vue` | Hide Roles tab for session user |

## Implementation Details

### 1. Members.vue - Add role field and dropdown

#### a) Add role to memberForm type and initial state

- Add `role?: string` to `Member` type
- Add `role: ''` to `memberForm` initial value (around line 302)

#### b) Add roleOptions

Add new computed/const for role dropdown options:

```typescript
const roleOptions = [
  { label: 'No Role', value: '' },
  { label: 'Moderator', value: 'Moderator' },
  { label: 'Course Creator', value: 'Course Creator' },
  { label: 'Batch Evaluator', value: 'Batch Evaluator' },
  { label: 'LMS Student', value: 'LMS Student' },
]
```

#### c) Update editMember function

Include role when populating form:

```typescript
const editMember = (member: Member) => {
  editingMember.value = member
  memberForm.value = {
    email: member.name,
    full_name: member.full_name,
    lms_store: member.lms_store || '',
    store_rank: member.store_rank || '',
    role: member.role || '',  // NEW FIELD
  }
  showMemberDialog.value = true
}
```

#### d) Add role dropdown to dialog

Add after `store_rank` Link field (around line 179):

```vue
<FormControl
  v-model="memberForm.role"
  :label="__('Role')"
  type="select"
  :options="roleOptions"
  class="w-full"
/>
```

#### e) Add updateRole resource

Add new resource to call the existing save_role API:

```typescript
const updateRole = createResource({
  url: 'lms.lms.api.save_role',
  auto: false,
  onSuccess() {
    toast.success(__('Role updated successfully'))
  },
  onError(error) {
    console.error('Error updating role:', error)
    toast.error(__('Failed to update role'))
  },
})
```

#### f) Update saveMember function

When role changes, call updateRole after member is created/updated:

```typescript
const saveMember = async () => {
  try {
    if (editingMember.value) {
      await updateMember.submit()
    } else {
      await createMember.submit()
    }
    
    // Handle role assignment
    if (memberForm.value.role) {
      updateRole.submit({
        user: memberForm.value.email,
        role: memberForm.value.role,
        value: true,
      })
    }
  } catch (error) {
    console.error('Error saving member:', error)
  }
}
```

#### g) Import toast for notifications

Add `toast` to the imports from 'frappe-ui':

```typescript
import {
  Avatar,
  Button,
  Breadcrumbs,
  ListView,
  ListHeader,
  ListHeaderItem,
  ListRows,
  ListRow,
  ListRowItem,
  Dialog,
  FormControl,
  createResource,
  toast,  // ADD THIS
} from 'frappe-ui'
```

### 2. Profile.vue - Prevent self-assignment

**File:** `frontend/src/pages/Profile.vue`

**Line 199:** Change from:

```javascript
if ($user.data?.is_moderator) buttons.push({ label: 'Roles' })
```

To:

```javascript
if ($user.data?.is_moderator && !isSessionUser()) buttons.push({ label: 'Roles' })
```

This ensures the Roles tab only appears when viewing another user's profile, not your own.

## Backend

No changes required.

The `save_role` API at `lms.lms.api.save_role` already exists in `lms/lms/api.py:1131`:

```python
@frappe.whitelist()
def save_role(user, role, value):
    frappe.only_for("Moderator")
    if cint(value):
        doc = frappe.get_doc(
            {
                "doctype": "Has Role",
                "parent": user,
                "role": role,
                "parenttype": "User",
                "parentfield": "roles",
            }
        )
        doc.save(ignore_permissions=True)
    else:
        frappe.db.delete("Has Role", {"parent": user, "role": role})
    return True
```

This API:
- Requires Moderator role to call
- Handles both assigning and removing roles
- Already validates permissions

## Requirements Summary

1. Role dropdown available when adding new member
2. Role dropdown available when editing existing member
3. Admin can see all 4 roles in dropdown
4. Prevent users from modifying their own roles via Profile page

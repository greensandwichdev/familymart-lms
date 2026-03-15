# Force Password Reset on First Login

## Requirement

When a new member is created from the Member Management menu:
1. Set temporary password to `"FamilyMartLMS123#"` 
2. Force user to change password immediately after first login
3. User cannot bypass the password change page even by typing a specific URL
4. After password change, user can access LMS dashboard

## Problem

Currently, when admin creates a new member from Member Management:
- Password is randomly generated (10 characters)
- Password is NOT displayed or sent to anyone
- New member cannot log in

## Solution Overview

### Approach: Custom Force Password Change with Custom Field

Since Frappe's built-in `force_user_to_reset_password()` relies on System Settings configuration which may not be set, we implement a custom solution:

1. **Add custom field** `force_password_change` to User doctype
2. **Set flag to 1** when creating new member
3. **Redirect to password change page** in `on_login` hook if flag is set
4. **Clear flag after password change** using custom update-password handler

---

## Implementation Details

### 1. Add Custom Field to User (fixtures/custom_field.json)

Add `force_password_change` field to User doctype:

```json
{
    "dt": "User",
    "fieldname": "force_password_change",
    "fieldtype": "Check",
    "label": "Force Password Change",
    "default": "0",
    "hidden": 1
}
```

### 2. Modify create_member (lms/lms/lms/store.py)

Set `force_password_change = 1` when creating member:

```python
frappe.db.set_value("User", email, "force_password_change", 1)
```

### 3. Modify on_login Hook (lms/lms/lms/user.py)

Check custom field and redirect to password change page:

```python
def on_login(login_manager):
    # Check if user needs to force password change
    if frappe.db.get_value("User", login_manager.user, "force_password_change"):
        frappe.local.response["redirect_to"] = "/update-password"
        frappe.local.response["message"] = "Password Reset"
        return
    
    # ... rest of existing code ...
```

### 4. Create Custom Password Change Handler (lms/lms/www/update-password.py)

Create custom handler that clears the flag after successful password change:

```python
def get_context(context):
    # Check if user is logged in and has force_password_change flag
    if frappe.session.user != "Guest":
        # Let Frappe handle the form normally
        pass
    # After password is changed, clear the force_password_change flag
    # This would be done via a hook or by modifying the form submission
```

---

## How It Works

1. **Admin creates member** from Member Management page
2. **User is created** with password `"FamilyMartLMS123#"`
3. **`force_password_change`** flag is set to `1`
4. **User logs in** with default password
5. **`on_login` hook** checks `force_password_change` flag
6. **If 1**, user is redirected to `/update-password`
7. **User changes password** on the page
8. **After password change**, the flag is cleared (`force_password_change = 0`)
9. **User can now access** LMS dashboard normally

---

## Files to Modify

| # | File | Change |
|---|------|--------|
| 1 | `lms/lms/fixtures/custom_field.json` | Add `force_password_change` field to User |
| 2 | `lms/lms/lms/store.py` | Set `force_password_change = 1` in `create_member()` |
| 3 | `lms/lms/lms/user.py` | Modify `on_login` to check flag and redirect |
| 4 | `lms/lms/www/update-password.py` | Create custom handler to clear flag after change |

---

## Alternative Approaches Considered

### Built-in Frappe Force Password (Rejected)
- Uses System Settings configuration which may not be set
- Less reliable for this use case

### Send Reset Email (Rejected)
- Requires email configuration
- More complex setup
- Adds extra step for user

---

## Status

- [ ] Add custom field to User doctype
- [ ] Modify create_member() to set flag
- [ ] Modify on_login hook to redirect
- [ ] Create custom update-password handler
- [ ] Test end-to-end flow

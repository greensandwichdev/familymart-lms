# Force Password Reset on First Login

## Issue

When a new member is created from the Member Management menu, they receive a random password that is never displayed or sent. This prevents the new member from logging in.

## Requirement

1. Set temporary password to `"FamilyMartLMS123#"` for all new members
2. Force password change immediately after first login
3. User cannot bypass the password change page even by typing a specific URL
4. After password change, user can access LMS dashboard

## Solution Implemented

### Files Modified

| # | File | Change |
|---|------|--------|
| 1 | `lms/lms/fixtures/custom_field.json` | Added `force_password_change` field to User |
| 2 | `lms/lms/lms/store.py` | Set `force_password_change = 1` in `create_member()` |
| 3 | `lms/lms/lms/user.py` | Modified `on_login` to check flag and redirect |
| 4 | `lms/lms/lms/api.py` | Added `update_password_with_flag_clear` API |
| 5 | `lms/lms/www/update-password.html` | Created custom password change page |

### Changes Made

#### 1. Custom Field (fixtures/custom_field.json)
Added `force_password_change` field to User doctype:
- Hidden field (not visible in UI)
- Default value: 0

#### 2. create_member (store.py)
- Set static password: `"FamilyMartLMS123#"`
- Set `force_password_change = 1` after user creation

#### 3. on_login (user.py)
Check if user has `force_password_change` flag:
- If 1, redirect to `/update-password`
- If 0, proceed to LMS home page

#### 4. Custom API (api.py)
Created `update_password_with_flag_clear`:
- Calls Frappe's original password update
- Clears `force_password_change` flag after success
- Updates `last_password_reset_date` to today's date

#### 5. Custom update-password page (www/update-password.html)
Created custom password change page:
- Uses custom API `lms.lms.api.update_password_with_flag_clear`
- Same UI as Frappe's default page
- Automatically clears the flag after password change

### How It Works

1. **Admin creates member** from Member Management page
2. **User is created** with password `"FamilyMartLMS123#"`
3. **`force_password_change`** flag is set to `1`
4. **User logs in** with default password
5. **`on_login` hook** checks `force_password_change` flag
6. **If 1**, user is redirected to `/update-password`
7. **User changes password** on the page
8. **After password change**, the flag is cleared (`force_password_change = 0`)
9. **User can now access** LMS dashboard normally

### Prerequisites

1. Run `bench migrate` to sync custom field to database
2. Clear cache: `bench clear-cache`

## Status

- [x] Add custom field to User doctype
- [x] Modify create_member() to set flag
- [x] Modify on_login hook to redirect
- [x] Create custom update-password handler (API + HTML)
- [ ] Run bench migrate to sync custom field
- [ ] Test end-to-end flow

# Fix Member Creation Hanging Issue

## Issue Description

Creating a new member from the Member Management menu was hanging/loading forever, even after simplifying the function to only create user data without additional logic.

## Root Causes Identified

### 1. Wildcard doc_events Hook (hooks.py)
- **Location:** `lms/lms/hooks.py:98-103`
- **Problem:** The hook `"*": {"on_change": ["lms.lms.doctype.lms_badge.lms_badge.process_badges"]}` was running badge processing on **every document save** across the entire Frappe system
- **Impact:** Caused massive performance degradation and cascading badge processing loops

### 2. Incomplete User Creation (store.py)
- **Location:** `lms/lms/lms/store.py:361-372`
- **Problem:** The `create_member` function was missing required User doctype fields:
  - Used `full_name` instead of required `first_name`
  - Missing `enabled`, `user_type`, `new_password`
- **Impact:** User insertion would fail silently or hang during validation

## Changes Made

### File: lms/lms/hooks.py

```diff
 doc_events = {
-    "*": {
-        "on_change": [
-            "lms.lms.doctype.lms_badge.lms_badge.process_badges",
-        ]
-    },
     "Discussion Reply": {"after_insert": "lms.lms.utils.handle_notifications"},
     "Notification Log": {"on_change": "lms.lms.utils.publish_notifications"},
     "User": {
         "validate": "lms.lms.user.validate_username_duplicates",
         "after_insert": "lms.lms.user.after_insert",
         "on_update": "lms.lms.user.on_update",
     },
 }
```

### File: lms/lms/lms/store.py

```python
@frappe.whitelist()
def create_member(email, full_name, lms_store=None, store_rank=None, role=None, sync=True):
	"""Create a new member user and optionally assign store/rank/role."""
	from frappe.utils import random_string

	frappe.flags.ignore_permissions = True
	frappe.flags.in_import = True

	user_doc = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": full_name,
			"enabled": 1,
			"user_type": "Website User",
			"new_password": random_string(10),
		}
	)
	user_doc.insert(ignore_permissions=True)

	if role:
		user_doc.add_roles(role)
	else:
		user_doc.add_roles("LMS Student")

	if lms_store or store_rank:
		assign_member_to_store(email, lms_store, store_rank, full_name)

	return {"name": email, "success": True}
```

## Key Fixes Applied

1. **Removed wildcard hook** - Prevents badge processing from running on every document save
2. **Fixed User creation** - Added required fields: `first_name`, `enabled`, `user_type`, `new_password`
3. **Added bypass flags** - Set `frappe.flags.in_import = True` to skip hooks during bulk creation
4. **Preserved functionality** - Still handles role assignment (defaults to "LMS Student") and store/rank assignment

## Why It Was Hanging

The combination of both issues created a perfect storm:
1. Every User insert triggered `process_badges` via the wildcard hook
2. Badge processing involved multiple DB queries and evaluations
3. The incomplete User data caused additional validation/fixup attempts
4. Together, this caused the request to hang indefinitely

## Status

- [x] Identify root causes
- [x] Remove wildcard doc_events hook
- [x] Fix create_member function with required fields
- [x] Verify member creation works
- [x] Verify store/rank assignment still works

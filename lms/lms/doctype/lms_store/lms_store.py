# Copyright (c) 2026, Frappe and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LMSStore(Document):
	pass


@frappe.whitelist()
def get_link_query(doctype, txt, searchfield, start, page_len, filters):
	"""Dynamic query method for Link field - filters by user's organization."""
	user = frappe.session.user
	if user == "Guest":
		return []

	roles = frappe.get_roles(user)
	user_info = frappe.db.get_value(
		"User",
		user,
		["organization", "lms_store"],
		as_dict=1,
	)

	query_filters = {"is_active": 1}

	# System Manager: see all stores
	if "System Manager" not in roles:
		if "Store Manager" in roles:
			# Store Manager: see only their own store
			if user_info and user_info.lms_store:
				query_filters["name"] = user_info.lms_store
			else:
				return []
		elif user_info and user_info.organization:
			# Brand Admin: see stores in their organization
			query_filters["organization"] = user_info.organization
		else:
			return []

	# Add search filter if txt provided
	if txt:
		query_filters["store_name"] = ["like", f"%{txt}%"]

	stores = frappe.get_all(
		"LMS Store",
		filters=query_filters,
		fields=["name", "store_name"],
		start=start,
		page_length=page_len
	)

	# Format for search_link API - needs value and label
	return [{"value": s.name, "label": s.store_name} for s in stores]

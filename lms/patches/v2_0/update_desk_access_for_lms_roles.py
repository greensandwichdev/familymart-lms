import frappe


def execute():
	roles = ["Course Creator", "Moderator", "Batch Evaluator", "LMS Student", "Brand Admin", "Store Manager"]

	for role in roles:
		if frappe.db.exists("Role", role):
			frappe.db.set_value("Role", role, "desk_access", 0)

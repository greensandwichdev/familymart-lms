import frappe
from frappe.model.document import Document


class Regency(Document):
	pass


def on_delete_regency(doc, method):
	if frappe.flags.in_install == "frappe":
		return

	districts = frappe.get_all("District", {"regency": doc.name}, pluck="name")
	for district in districts:
		frappe.delete_doc("District", district, ignore_permissions=True)

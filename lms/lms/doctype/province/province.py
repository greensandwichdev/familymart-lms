import frappe
from frappe.model.document import Document


class Province(Document):
	pass


def on_delete_province(doc, method):
	if frappe.flags.in_install == "frappe":
		return

	regencies = frappe.get_all("Regency", {"province": doc.name}, pluck="name")
	for regency in regencies:
		frappe.delete_doc("Regency", regency, ignore_permissions=True)

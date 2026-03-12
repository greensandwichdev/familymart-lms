"""API methods for Store Management."""

import frappe
from frappe import _


@frappe.whitelist()
def get_stores():
	"""Returns the list of active stores."""
	stores = frappe.get_all(
		"LMS Store",
		filters={"is_active": 1},
		fields=[
			"name",
			"store_name",
			"store_code",
			"organization",
			"address",
			"province",
			"regency",
			"district",
		],
		order_by="store_name",
	)

	for store in stores:
		if store.district:
			district_doc = frappe.get_doc("District", store.district)
			store.district = district_doc.district_name

	return stores


@frappe.whitelist()
def get_store(store):
	"""Returns the store details."""
	store_doc = frappe.get_doc("LMS Store", store)
	return {
		"name": store_doc.name,
		"store_name": store_doc.store_name,
		"store_code": store_doc.store_code,
		"organization": store_doc.organization,
		"address": store_doc.address,
		"is_active": store_doc.is_active,
	}


@frappe.whitelist()
def create_store(data):
	"""Creates a new store."""
	if isinstance(data, str):
		data = frappe.parse_json(data)

	store = frappe.get_doc({"doctype": "LMS Store"})
	store.update(data)
	store.insert()
	return store.name


@frappe.whitelist()
def update_store(store, data):
	"""Updates an existing store."""
	if isinstance(data, str):
		data = frappe.parse_json(data)

	store_doc = frappe.get_doc("LMS Store", store)
	store_doc.update(data)
	store_doc.save()
	return store_doc.name


@frappe.whitelist()
def delete_store(store):
	"""Soft deletes a store by setting is_active to 0."""
	frappe.db.set_value("LMS Store", store, "is_active", 0)


@frappe.whitelist()
def get_store_members(store):
	"""Returns the list of members in a store."""
	members = frappe.get_all(
		"User",
		filters={"lms_store": store},
		fields=["name", "full_name", "email", "store_rank", "enabled"],
		order_by="full_name",
	)

	for member in members:
		if member.store_rank:
			rank_doc = frappe.get_doc("Store Rank", member.store_rank)
			member["rank_name"] = rank_doc.rank_name
			member["rank_order"] = rank_doc.rank_order

	return members


@frappe.whitelist()
def get_store_ranks():
	"""Returns the list of store ranks."""
	ranks = frappe.get_all(
		"Store Rank",
		fields=["name", "rank_name", "rank_code", "rank_order"],
		order_by="rank_order desc",
	)
	return ranks


@frappe.whitelist()
def assign_member_to_store(member, store, rank, full_name=None):
	"""Assigns a user to a store with a rank."""
	if not rank:
		frappe.throw("Store Rank is mandatory")

	frappe.db.set_value("User", member, "lms_store", store)
	frappe.db.set_value("User", member, "store_rank", rank)
	if full_name is not None:
		frappe.db.set_value("User", member, "full_name", full_name)

	sync_programs_for_rank(rank)

	return {
		"member": member,
		"store": store,
		"rank": rank,
	}


def sync_programs_for_rank(rank):
	"""Sync all programs that have the given rank configured."""
	programs = frappe.get_all(
		"LMS Program",
		fields=["name"],
		filters=[
			["LMS Program Rank", "store_rank", "=", rank]
		],
	)

	for prog in programs:
		try:
			from lms.lms.api import sync_program_members_by_ranks
			sync_program_members_by_ranks(prog.name)
		except Exception as e:
			frappe.log_error(f"Failed to sync program {prog.name}: {str(e)}")


@frappe.whitelist()
def update_member_rank(member, rank, full_name=None):
	"""Updates a member's rank and optionally their full name."""
	if not rank:
		frappe.throw("Store Rank is mandatory")

	frappe.db.set_value("User", member, "store_rank", rank)
	if full_name is not None:
		frappe.db.set_value("User", member, "full_name", full_name)

	sync_programs_for_rank(rank)

	return {"member": member, "rank": rank}


@frappe.whitelist()
def remove_member_from_store(member):
	"""Removes a member from their store."""
	frappe.db.set_value("User", member, "lms_store", None)
	frappe.db.set_value("User", member, "store_rank", None)
	return {"member": member}


@frappe.whitelist()
def get_user_store_info():
	"""Returns the current user's store and rank information."""
	user = frappe.session.user
	if user == "Guest":
		return {}

	user_doc = frappe.get_doc("User", user)
	return {
		"store": user_doc.lms_store,
		"store_rank": user_doc.store_rank,
		"has_store": bool(user_doc.lms_store),
		"has_rank": bool(user_doc.store_rank),
	}


@frappe.whitelist()
def get_provinces():
	"""Returns the list of all provinces."""
	provinces = frappe.get_all("Province", order_by="name")
	return provinces


@frappe.whitelist()
def get_regencies(province=None):
	"""Returns the list of regencies in a province."""
	province = province or frappe.form_dict.get("province")
	if not province:
		return []

	regencies = frappe.get_all(
		"Regency",
		filters={"province": province},
		order_by="name",
	)
	return regencies


@frappe.whitelist()
def get_districts(regency=None):
	"""Returns the list of districts in a regency."""
	regency = regency or frappe.form_dict.get("regency")
	if not regency:
		return []

	districts = frappe.get_all(
		"District",
		filters={"regency": regency},
		order_by="name",
	)
	return districts

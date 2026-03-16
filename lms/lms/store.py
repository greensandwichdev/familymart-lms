"""API methods for Store Management."""

import frappe
from frappe import _


@frappe.whitelist()
def get_stores():
	"""Returns the list of active stores based on user access."""
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

	filters = {"is_active": 1}

	# System Manager: see all stores
	if "System Manager" not in roles:
		if "Store Manager" in roles:
			# Store Manager: see only their own store
			if user_info and user_info.lms_store:
				filters["name"] = user_info.lms_store
			else:
				return []
		elif user_info and user_info.organization:
			# Brand Admin: see stores in their organization
			filters["organization"] = user_info.organization
		else:
			# No access - user has no org and no store manager role
			return []

	stores = frappe.get_all(
		"LMS Store",
		filters=filters,
		fields=[
			"name",
			"store_name",
			"store_code",
			"organization",
			"address",
			"image",
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
def get_stores_with_member_count():
	"""Returns list of stores with member counts based on user access."""
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

	filters = {"is_active": 1}

	# System Manager: see all stores
	if "System Manager" not in roles:
		if "Store Manager" in roles:
			# Store Manager: see only their own store
			if user_info and user_info.lms_store:
				filters["name"] = user_info.lms_store
			else:
				return []
		elif user_info and user_info.organization:
			# Brand Admin: see stores in their organization
			filters["organization"] = user_info.organization
		else:
			# No access
			return []

	stores = frappe.get_all(
		"LMS Store",
		filters=filters,
		fields=[
			"name",
			"store_name",
			"store_code",
			"organization",
			"address",
			"image",
			"province",
			"regency",
			"district",
			"is_active",
		],
		order_by="store_name",
	)

	for store in stores:
		store["member_count"] = frappe.db.count("User", {"lms_store": store.name})
		if store.district:
			district_doc = frappe.get_doc("District", store.district)
			store.district = district_doc.district_name

	return stores


@frappe.whitelist()
def get_store_details(store):
	"""Returns comprehensive store details including members and analytics."""
	store_doc = frappe.get_doc("LMS Store", store)

	province_name = store_doc.province
	regency_name = store_doc.regency
	district_name = store_doc.district

	if province_name:
		province_doc = frappe.get_doc("Province", province_name)
		province_name = province_doc.name

	if regency_name:
		regency_doc = frappe.get_doc("Regency", regency_name)
		regency_name = regency_doc.name

	if district_name:
		district_doc = frappe.get_doc("District", district_name)
		district_name = district_doc.district_name

	members = frappe.get_all(
		"User",
		filters={"lms_store": store},
		fields=["name", "full_name", "email", "store_rank", "enabled"],
		order_by="full_name",
	)

	for m in members:
		if m.store_rank:
			rank_doc = frappe.get_doc("Store Rank", m.store_rank)
			m.rank_name = rank_doc.rank_name
			m.rank_order = rank_doc.rank_order
		else:
			m.rank_name = None
			m.rank_order = 0

	member_stats = {}
	for m in members:
		rank = m.rank_name or "No Rank"
		member_stats[rank] = member_stats.get(rank, 0) + 1

	member_names = [m.name for m in members]
	enrollments = []
	program_stats = {}
	total_enrollments = 0
	completed_enrollments = 0
	in_progress_enrollments = 0

	if member_names:
		enrollments = frappe.get_all(
			"LMS Program Member",
			filters={"member": ["in", member_names]},
			fields=["member", "parent", "progress", "full_name"],
		)

		program_names = list(set([e.parent for e in enrollments]))
		for prog_name in program_names:
			prog_enrollments = [e for e in enrollments if e.parent == prog_name]
			prog_completed = len([e for e in prog_enrollments if e.progress == 100])
			prog_in_progress = len([e for e in prog_enrollments if 0 < e.progress < 100])
			program_stats[prog_name] = {
				"total": len(prog_enrollments),
				"completed": prog_completed,
				"in_progress": prog_in_progress,
				"not_started": len(prog_enrollments) - prog_completed - prog_in_progress,
			}

		total_enrollments = len(enrollments)
		completed_enrollments = len([e for e in enrollments if e.progress == 100])
		in_progress_enrollments = len([e for e in enrollments if 0 < e.progress < 100])

	return {
		"name": store_doc.name,
		"store_name": store_doc.store_name,
		"store_code": store_doc.store_code,
		"organization": store_doc.organization,
		"address": store_doc.address,
		"image": store_doc.image,
		"province": province_name,
		"regency": regency_name,
		"district": district_name,
		"is_active": store_doc.is_active,
		"members": members,
		"member_count": len(members),
		"member_stats": member_stats,
		"enrollments": enrollments,
		"program_stats": program_stats,
		"total_enrollments": total_enrollments,
		"completed_enrollments": completed_enrollments,
		"in_progress_enrollments": in_progress_enrollments,
		"not_started_enrollments": total_enrollments - completed_enrollments - in_progress_enrollments,
	}


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

	current_user = frappe.session.user
	current_user_org = frappe.db.get_value("User", current_user, "organization")

	frappe.db.set_value("User", member, "lms_store", store)
	frappe.db.set_value("User", member, "store_rank", rank)
	if full_name is not None:
		frappe.db.set_value("User", member, "full_name", full_name)

	if current_user_org:
		frappe.db.set_value("User", member, "organization", current_user_org)

	frappe.enqueue(
		"lms.lms.store.sync_programs_for_rank",
		rank=rank,
		queue="short",
		timeout=300,
		enqueue_after_commit=True,
	)

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
		filters=[["LMS Program Rank", "store_rank", "=", rank]],
	)

	for prog in programs:
		try:
			from lms.lms.api import sync_program_members_by_ranks

			sync_program_members_by_ranks(prog.name)
		except Exception as e:
			frappe.log_error(f"Failed to sync program {prog.name}: {str(e)}")


@frappe.whitelist()
def update_member_rank(member, rank=None, full_name=None, store=None):
	"""Updates a member's store, rank and optionally their full name."""
	if store is not None:
		frappe.db.set_value("User", member, "lms_store", store or None)
	if rank is not None:
		frappe.db.set_value("User", member, "store_rank", rank or None)
	if full_name is not None:
		frappe.db.set_value("User", member, "full_name", full_name)

	if rank:
		frappe.enqueue(
			"lms.lms.store.sync_programs_for_rank",
			rank=rank,
			queue="short",
			timeout=300,
			enqueue_after_commit=True,
		)

	return {"member": member, "store": store, "rank": rank}


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


@frappe.whitelist()
def create_member(email, full_name, lms_store=None, store_rank=None, role=None, sync=True):
	"""Create a new member user and optionally assign store/rank/role."""
	frappe.flags.ignore_permissions = True
	frappe.flags.in_import = True

	user_doc = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": full_name,
			"enabled": 1,
			"user_type": "Website User",
			"new_password": "FamilyMartLMS123#",
		}
	)
	user_doc.insert(ignore_permissions=True)

	frappe.db.set_value("User", email, "last_password_reset_date", "2020-01-01")
	frappe.db.set_value("User", email, "force_password_change", 1)

	user_doc.reload()

	if role:
		user_doc.add_roles(role)
	else:
		user_doc.add_roles("LMS Student")

	if lms_store or store_rank:
		assign_member_to_store(email, lms_store, store_rank, full_name)

	return {"name": email, "success": True}

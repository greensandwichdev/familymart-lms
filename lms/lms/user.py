import frappe
from frappe import _
from frappe.model.naming import append_number_if_name_exists
from frappe.utils import escape_html, random_string
from frappe.website.utils import cleanup_page_name, is_signup_disabled

from lms.lms.utils import get_country_code


def validate_username_duplicates(doc, method):
	while not doc.username or doc.username_exists():
		doc.username = append_number_if_name_exists(
			doc.doctype, cleanup_page_name(doc.full_name), fieldname="username"
		)
	if " " in doc.username:
		doc.username = doc.username.replace(" ", "")

	if len(doc.username) < 4:
		doc.username = doc.email.replace("@", "").replace(".", "")


def after_insert(doc, method):
	"""Saat user pertama kali dibuat"""
	try:
		# Skip if in bulk import mode
		if frappe.flags.get("in_import"):
			return

		# TEMPORARILY DISABLED FOR DEBUG
		# # ✅ Tambahkan role LMS Student (jika belum ada)
		# if "LMS Student" not in [r.role for r in doc.get("roles") or []]:
		#     doc.add_roles("LMS Student")
		#     frappe.logger().info(f"[AUTO-ROLE] Role LMS Student ditambahkan ke {doc.name}")

		# 🔄 Jadwalkan sinkronisasi enrollment rank secara async
		# TEMPORARILY DISABLED FOR DEBUG - uncomment after testing
		# frappe.enqueue(
		#     "lms.lms.user.sync_user_program_by_rank",
		#     user_name=doc.name,
		#     queue="short",
		#     timeout=300,
		#     enqueue_after_commit=True,
		#     now=frappe.in_test,
		# )

	except Exception:
		frappe.log_error(frappe.get_traceback(), "Auto role & enroll after_insert User")


def on_update(doc, method):
	"""Saat user diupdate"""
	try:
		# Skip if in bulk import mode
		if frappe.flags.get("in_import"):
			return

		# Hanya jalankan jika store_rank atau enabled berubah
		if doc.has_value_changed("store_rank") or doc.has_value_changed("enabled"):
			# TEMPORARILY DISABLED FOR DEBUG - uncomment after testing
			# frappe.enqueue(
			#     "lms.lms.user.sync_user_program_by_rank",
			#     user_name=doc.name,
			#     queue="short",
			#     timeout=300,
			#     enqueue_after_commit=True,
			#     now=frappe.in_test,
			# )
			pass
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Auto-enroll & sync rank on_update User")


def sync_user_program_by_rank(user_name):
	"""Sinkronisasi keanggotaan program berdasarkan store_rank user"""
	try:
		doc = frappe.get_doc("User", user_name)

		if doc.store_rank and doc.enabled:
			matched_programs = set()
			programs = frappe.get_all("LMS Program", fields=["name", "title"])

			for p in programs:
				program = frappe.get_doc("LMS Program", p.name)

				# cek apakah program punya member template dengan rank ini
				for m in program.program_members:
					if m.store_rank == doc.store_rank:
						matched_programs.add(program.name)

						# cek apakah user sudah jadi member program ini
						member_name = frappe.db.exists(
							"LMS Program Member", {"parent": program.name, "member": doc.name}
						)

						if member_name:
							# update rank jika berbeda
							current_rank = frappe.db.get_value(
								"LMS Program Member", member_name, "store_rank"
							)
							if current_rank != doc.store_rank:
								frappe.db.set_value(
									"LMS Program Member", member_name, {"store_rank": doc.store_rank}
								)
								frappe.logger().info(
									f"[AUTO-UPDATE] Rank user {doc.full_name} diupdate di {program.title}"
								)
						else:
							# tambahkan user baru
							program.append(
								"program_members",
								{
									"member": doc.name,
									"store_rank": doc.store_rank,
									"full_name": doc.full_name,
									"progress": 0,
								},
							)
							program.save(ignore_permissions=True)
							frappe.logger().info(f"User {doc.full_name} otomatis masuk ke {program.title}")
						break

			# 🔽 Hapus dari program lain yang tidak cocok rank-nya
			memberships = frappe.get_all(
				"LMS Program Member", filters={"member": doc.name}, fields=["name", "parent", "store_rank"]
			)

			for m in memberships:
				if m.parent not in matched_programs:
					frappe.db.delete("LMS Program Member", {"name": m.name})
					frappe.logger().info(
						f"[AUTO-REMOVE] {doc.full_name} dihapus dari {m.parent} (rank tidak cocok)"
					)

			frappe.db.commit()

		else:
			# ❌ Jika user nonaktif atau tidak punya rank — hapus semua membership
			frappe.db.delete("LMS Program Member", {"member": doc.name})
			frappe.logger().info(
				f"[AUTO-CLEANUP] {doc.full_name} dihapus dari semua program (nonaktif / tanpa rank)"
			)
			frappe.db.commit()

	except Exception:
		frappe.log_error(frappe.get_traceback(), "sync_user_program_by_rank Error")


@frappe.whitelist(allow_guest=True)
def sign_up(email, full_name, verify_terms, user_category):
	if is_signup_disabled():
		frappe.throw(_("Sign Up is disabled"), _("Not Allowed"))

	user = frappe.db.get("User", {"email": email})
	if user:
		if user.enabled:
			return 0, _("Already Registered")
		else:
			return 0, _("Registered but disabled")
	else:
		if frappe.db.get_creation_count("User", 60) > 300:
			frappe.respond_as_web_page(
				_("Temporarily Disabled"),
				_(
					"Too many users signed up recently, so the registration is disabled. Please try back in an hour"
				),
				http_status_code=429,
			)

	user = frappe.get_doc(
		{
			"doctype": "User",
			"email": email,
			"first_name": escape_html(full_name),
			"verify_terms": verify_terms,
			"user_category": user_category,
			"country": "",
			"enabled": 1,
			"new_password": random_string(10),
			"user_type": "Website User",
		}
	)
	user.flags.ignore_permissions = True
	user.flags.ignore_password_policy = True
	user.insert()

	# set default signup role as per Portal Settings
	default_role = frappe.db.get_single_value("Portal Settings", "default_role")
	if default_role:
		user.add_roles(default_role)

	user.add_roles("LMS Student")
	set_country_from_ip(None, user.name)

	if user.flags.email_sent:
		return 1, _("Please check your email for verification")
	else:
		return 2, _("Please ask your administrator to verify your sign-up")


def set_country_from_ip(login_manager=None, user=None):
	if not user and login_manager:
		user = login_manager.user
	user_country = frappe.db.get_value("User", user, "country")
	if user_country:
		return
	frappe.db.set_value("User", user, "country", get_country_code())
	return


def on_login(login_manager):
	import frappe

	frappe.logger().info(f"DEBUG: on_login called for user: {login_manager.user}")

	roles = frappe.get_roles(login_manager.user)

	if "Store Manager" in roles:
		frappe.local.response["home_page"] = "/lms"
		frappe.local.response["redirect_to"] = "/lms"
		return

	user_rank = frappe.db.get_value("User", login_manager.user, "store_rank")
	if user_rank:
		rank_name = frappe.db.get_value("Store Rank", user_rank, "rank_name")
		if rank_name in ["SPV", "Staff"]:
			frappe.local.response["home_page"] = "/lms"
			frappe.local.response["redirect_to"] = "/lms"
			return

	force_pwd = frappe.db.get_value("User", login_manager.user, "force_password_change")
	frappe.logger().info(f"DEBUG: force_password_change = {force_pwd}")

	# Check if user needs to force password change
	if force_pwd:
		frappe.logger().info("DEBUG: Setting redirect to /update-password")
		frappe.local.response["redirect_to"] = "/update-password"
		frappe.local.response["home_page"] = "/update-password"
		frappe.local.response["message"] = "Password Reset"
		return

	default_app = frappe.db.get_single_value("System Settings", "default_app")
	if default_app == "lms":
		frappe.local.response["home_page"] = "/lms"

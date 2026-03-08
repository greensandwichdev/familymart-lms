"""
Migration script to copy crew_rank values to store_rank.

This script migrates data from the old crew_rank field to the new store_rank field
for both User doctype and LMS Program Member doctype.

Run with: bench --site [site] execute lms.lms.patches.store_rank_migration.run
"""

import frappe


def run():
	print("Starting store_rank migration...")

	# Migrate User doctype
	migrate_user_ranks()

	# Migrate LMS Program Member
	migrate_program_member_ranks()

	frappe.db.commit()
	print("Migration completed successfully!")


def migrate_user_ranks():
	"""Copy crew_rank values to store_rank for User doctype."""
	print("\n[1/2] Migrating User ranks...")

	users = frappe.get_all("User", filters={"crew_rank": ["is", "set"]}, fields=["name", "crew_rank"])

	updated_count = 0
	for user in users:
		frappe.db.set_value("User", user.name, "store_rank", user.crew_rank)
		updated_count += 1

	print(f"   Updated {updated_count} User records")


def migrate_program_member_ranks():
	"""Copy crew_rank values to store_rank for LMS Program Member."""
	print("\n[2/2] Migrating LMS Program Member ranks...")

	members = frappe.get_all(
		"LMS Program Member", filters={"crew_rank": ["is", "set"]}, fields=["name", "crew_rank"]
	)

	updated_count = 0
	for member in members:
		frappe.db.set_value("LMS Program Member", member.name, "store_rank", member.crew_rank)
		updated_count += 1

	print(f"   Updated {updated_count} LMS Program Member records")


if __name__ == "__main__":
	run()

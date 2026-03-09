import frappe
import csv
import requests
from io import StringIO


def execute():
	"""Import districts from Indonesia administrative data."""

	# Delete existing districts first
	print("Clearing existing districts...")
	frappe.db.delete("District")
	frappe.db.commit()

	# Download districts CSV
	url = "https://raw.githubusercontent.com/fityannugroho/idn-area-data/main/data/districts.csv"
	print("Downloading districts data from GitHub...")
	response = requests.get(url, timeout=60)
	response.raise_for_status()

	# Parse CSV
	reader = csv.DictReader(StringIO(response.text))
	districts = list(reader)

	total = len(districts)
	print(f"Found {total} districts")

	# Build regency code to name mapping
	regency_map = {}
	regencies = frappe.get_all("Regency", fields=["name", "code"])
	for r in regencies:
		regency_map[r.code] = r.name

	print(f"Loaded {len(regency_map)} regencies")

	created = 0
	skipped = 0
	batch_size = 100

	for idx, row in enumerate(districts):
		regency_code = row.get("regency_code", "")
		regency_name = regency_map.get(regency_code)

		if not regency_name:
			skipped += 1
			continue

		district_code = row.get("code", "")
		district_name = row.get("name", "")

		# Use code as name (unique ID), store actual name in district_name field
		doc = frappe.new_doc("District")
		doc.name = district_code
		doc.code = district_code
		doc.district_name = district_name
		doc.regency = regency_name

		try:
			doc.insert(ignore_permissions=True)
			created += 1
		except Exception as e:
			print(f"Error: Failed to insert district {district_name}: {str(e)}")
			skipped += 1

		if (idx + 1) % batch_size == 0:
			print(f"Importing... {idx + 1}/{total}")
			frappe.db.commit()

	frappe.db.commit()

	print(f"District import complete!")
	print(f"Created: {created}, Skipped: {skipped}, Total: {total}")

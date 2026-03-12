import frappe


def add_parent_columns(doctype, table_name):
    """Add missing parent columns to a child table if they don't exist."""
    if not frappe.db.exists("DocType", doctype):
        return False

    # Use backticks for table names with spaces
    try:
        columns = frappe.db.sql("DESCRIBE `{0}`".format(table_name))
        existing_cols = [col[0] for col in columns] if columns else []
    except Exception as e:
        print("Table {0} may not exist yet: {1}".format(table_name, str(e)))
        return False

    added_any = False

    if 'parent' not in existing_cols:
        frappe.db.sql("ALTER TABLE `{0}` ADD COLUMN `parent` VARCHAR(140)".format(table_name))
        print("Added 'parent' column to {0}".format(table_name))
        added_any = True

    if 'parenttype' not in existing_cols:
        frappe.db.sql("ALTER TABLE `{0}` ADD COLUMN `parenttype` VARCHAR(140)".format(table_name))
        print("Added 'parenttype' column to {0}".format(table_name))
        added_any = True

    if 'parentfield' not in existing_cols:
        frappe.db.sql("ALTER TABLE `{0}` ADD COLUMN `parentfield` VARCHAR(140)".format(table_name))
        print("Added 'parentfield' column to {0}".format(table_name))
        added_any = True

    if 'idx' not in existing_cols:
        frappe.db.sql("ALTER TABLE `{0}` ADD COLUMN `idx` INT DEFAULT 0".format(table_name))
        print("Added 'idx' column to {0}".format(table_name))
        added_any = True

    return added_any


def add_data_columns(doctype, table_name):
    """Add missing data columns based on DocType fields."""
    if not frappe.db.exists("DocType", doctype):
        return False

    try:
        columns = frappe.db.sql("DESCRIBE `{0}`".format(table_name))
        existing_cols = [col[0] for col in columns] if columns else []
    except Exception:
        return False

    doc = frappe.get_doc("DocType", doctype)
    added_any = False

    for field in doc.fields:
        if field.fieldname not in existing_cols:
            # Map fieldtype to MySQL column type
            fieldtype_map = {
                "Data": "VARCHAR(140)",
                "Small Text": "TEXT",
                "Long Text": "LONGTEXT",
                "Int": "INT",
                "Date": "DATE",
                "Datetime": "DATETIME",
                "Link": "VARCHAR(140)",
                "Check": "INT",
                "Float": "FLOAT",
                "Currency": "DECIMAL(18,6)",
            }
            col_type = fieldtype_map.get(field.fieldtype, "VARCHAR(140)")

            try:
                frappe.db.sql("ALTER TABLE `{0}` ADD COLUMN `{1}` {2}".format(
                    table_name, field.fieldname, col_type))
                print("Added '{1}' column to {0}".format(table_name, field.fieldname))
                added_any = True
            except Exception as e:
                print("Could not add column {0}: {1}".format(field.fieldname, str(e)))

    return added_any


def execute():
    # Fix Course Grade table - table name with space
    add_parent_columns("Course Grade", "tabCourse Grade")

    # Fix LMS Program Rank table - use correct table name
    add_parent_columns("LMS Program Rank", "tabLMS Program Rank")
    add_data_columns("LMS Program Rank", "tabLMS Program Rank")

    frappe.db.commit()
    print("All child table migrations complete!")

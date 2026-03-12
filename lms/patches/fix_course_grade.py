# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe

def run():
    # Check existing columns
    columns = frappe.db.sql("DESCRIBE `tabCourse Grade`")
    print("Current columns in tabCourse Grade:")
    for col in columns:
        print("  - {0}".format(col[0]))
    
    # Add missing parent columns
    existing_cols = [col[0] for col in columns]
    
    if 'parent' not in existing_cols:
        frappe.db.sql("ALTER TABLE `tabCourse Grade` ADD COLUMN `parent` VARCHAR(140)")
        print("Added 'parent' column")
    
    if 'parenttype' not in existing_cols:
        frappe.db.sql("ALTER TABLE `tabCourse Grade` ADD COLUMN `parenttype` VARCHAR(140)")
        print("Added 'parenttype' column")
    
    if 'parentfield' not in existing_cols:
        frappe.db.sql("ALTER TABLE `tabCourse Grade` ADD COLUMN `parentfield` VARCHAR(140)")
        print("Added 'parentfield' column")
    
    if 'idx' not in existing_cols:
        frappe.db.sql("ALTER TABLE `tabCourse Grade` ADD COLUMN `idx` INT DEFAULT 0")
        print("Added 'idx' column")
    
    frappe.db.commit()
    print("Done!")

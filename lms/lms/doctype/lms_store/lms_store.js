// Copyright (c) 2026, Frappe and contributors
// For license information, please see license.txt

frappe.ui.form.on("LMS Store", {
	province: function(frm) {
		frm.set_query("regency", function() {
			return {
				filters: [["Regency", "province", "=", frm.doc.province]]
			};
		});
		frm.set_value("regency", "");
		frm.set_value("district", "");
	},
	regency: function(frm) {
		frm.set_query("district", function() {
			return {
				filters: [["District", "regency", "=", frm.doc.regency]]
			};
		});
		frm.set_value("district", "");
	}
});

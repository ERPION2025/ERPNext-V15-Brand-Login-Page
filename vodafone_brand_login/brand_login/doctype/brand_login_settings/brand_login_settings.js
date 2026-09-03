// Copyright (c) 2026, Pranav Dixit / ERPion Technologies LLP
// License: MIT. See license.txt

frappe.ui.form.on("Brand Login Settings", {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.enabled) {
			const login_url = `${window.location.origin}/login?brand=${frm.doc.brand_key}`;
			frm.add_custom_button(__("Open Themed Login Page"), () => {
				window.open(login_url, "_blank");
			});
			frm.add_custom_button(__("Copy Shareable Link"), () => {
				const share_url = `${window.location.origin}/b/${frm.doc.brand_key}`;
				frappe.utils.copy_to_clipboard(share_url);
			});
		}
	},

	company(frm) {
		if (!frm.doc.company) return;

		// Pull display name + logo from the Company master so brand data
		// stays sourced from the Company master by default. The user can
		// still override business_name/logo manually afterwards.
		frappe.db.get_doc("Company", frm.doc.company).then((company) => {
			if (!frm.doc.business_name) {
				frm.set_value("business_name", company.company_name);
			}
			if (!frm.doc.logo && company.company_logo) {
				frm.set_value("logo", company.company_logo);
			}
			if (!frm.doc.brand_key) {
				frm.set_value("brand_key", company.company_name);
			}
		});
	},
});

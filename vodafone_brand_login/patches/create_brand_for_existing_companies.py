# Copyright (c) 2026, Pranav Dixit / ERPion Technologies LLP
# License: MIT. See license.txt

"""
Safety-net patch, run once via `bench migrate`. Covers the case where
Company records were created between `bench install-app` and the first
migrate, or where after_install did not run (e.g. the app was added to
apps.txt and the site rebuilt rather than freshly installed). Fully
idempotent - safe to run more than once.
"""

import frappe


def execute():
	from vodafone_brand_login.install import _create_default_vodafone_brand, _setup_global_settings
	from vodafone_brand_login.brand_login.doctype.brand_login_settings.brand_login_settings import (
		create_stub_for_company,
	)

	_setup_global_settings()
	_create_default_vodafone_brand()

	for company_name in frappe.get_all("Company", pluck="name"):
		if frappe.db.exists("Brand Login Settings", {"company": company_name}):
			continue
		company_doc = frappe.get_doc("Company", company_name)
		create_stub_for_company(company_doc)

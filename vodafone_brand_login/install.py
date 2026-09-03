# Copyright (c) 2026, Pranav Dixit / ERPion Technologies LLP
# License: MIT. See license.txt

import frappe


def after_install():
	_setup_global_settings()
	_create_default_vodafone_brand()
	_create_stubs_for_existing_companies()


def _setup_global_settings():
	settings = frappe.get_single("Brand Login Global Settings")
	if not settings.footer_text:
		settings.footer_text = "Powered by Vodafone X ERPNext"
	if not settings.fallback_business_name:
		settings.fallback_business_name = "Vodafone"
	if not settings.fallback_primary_color:
		settings.fallback_primary_color = "#E60000"
	if not settings.fallback_secondary_color:
		settings.fallback_secondary_color = "#FFFFFF"
	if not settings.fallback_accent_text_color:
		settings.fallback_accent_text_color = "#FFFFFF"
	if settings.show_business_switcher is None:
		settings.show_business_switcher = 1
	if not settings.cookie_expiry_days:
		settings.cookie_expiry_days = 30
	settings.save(ignore_permissions=True)


def _create_default_vodafone_brand():
	if frappe.db.exists("Brand Login Settings", "vodafone"):
		return

	doc = frappe.new_doc("Brand Login Settings")
	doc.brand_key = "vodafone"
	doc.business_name = "Vodafone"
	doc.tagline = "ERPNext, deployed by Vodafone"
	doc.is_default = 1
	doc.enabled = 1
	doc.show_in_switcher = 0  # it's the fallback, not a pickable "business"
	doc.primary_color = "#E60000"
	doc.secondary_color = "#FFFFFF"
	doc.accent_text_color = "#FFFFFF"
	doc.insert(ignore_permissions=True)


def _create_stubs_for_existing_companies():
	"""If this app is installed on a site that already has Company
	records (e.g. added to an existing deployment rather than a fresh
	site), back-fill a disabled Brand Login Settings stub for each one,
	the same way the after_insert doc_event does for new Companies."""
	from vodafone_brand_login.brand_login.doctype.brand_login_settings.brand_login_settings import (
		create_stub_for_company,
	)

	companies = frappe.get_all("Company", pluck="name")
	for company_name in companies:
		if frappe.db.exists("Brand Login Settings", {"company": company_name}):
			continue
		company_doc = frappe.get_doc("Company", company_name)
		create_stub_for_company(company_doc)

"""
Handler for the friendly business login link:  /b/<brand_key>

Registered via website_route_rules in hooks.py, mapping
/b/<brand_key>  ->  brand_redirect

This performs a plain HTTP redirect to /login?brand=<brand_key>. It does
not touch authentication in any way - it only exists so a business can be
given a short, memorable link (e.g. https://site.example.com/b/acme-salon)
instead of having to remember the query-string form.

If this route ever misbehaves on your Frappe version, it is safe to
delete this file and the corresponding website_route_rules entry in
hooks.py - every page still works fine with the plain
/login?brand=<brand_key> link.
"""

import frappe
from frappe import _


def get_context(context):
	brand_key = frappe.form_dict.get("brand_key")

	if not brand_key:
		raise frappe.Redirect("/login")

	# Basic sanitisation - brand_key should only ever be a slug we
	# generated ourselves (see brand_login_settings.py autoname/validate)
	brand_key = frappe.utils.strip_html(brand_key).strip()

	if not frappe.db.exists(
		"Brand Login Settings", {"brand_key": brand_key, "enabled": 1}
	):
		frappe.local.flags.redirect_location = "/login"
		raise frappe.Redirect

	frappe.local.flags.redirect_location = f"/login?brand={brand_key}"
	raise frappe.Redirect

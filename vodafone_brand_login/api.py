# Copyright (c) 2026, Pranav Dixit / ERPion Technologies LLP
# License: MIT. See license.txt

"""
Whitelisted, guest-accessible endpoints used by public/js/brand_login.js
on the pre-login pages. These only ever read/write Brand Login Settings
and Brand Login Global Settings - never anything else - and never touch
authentication.
"""

import frappe

COOKIE_NAME = "vbl_brand"

BRAND_FIELDS = [
	"brand_key",
	"business_name",
	"tagline",
	"primary_color",
	"secondary_color",
	"accent_text_color",
	"logo",
	"favicon",
]


def _file_url(value):
	"""Attach Image fields already store a servable URL/path - pass through."""
	return value or None


def _default_brand_dict():
	settings = frappe.get_cached_doc("Brand Login Global Settings")
	return {
		"brand_key": "vodafone",
		"business_name": settings.fallback_business_name or "Vodafone",
		"tagline": None,
		"primary_color": settings.fallback_primary_color or "#E60000",
		"secondary_color": settings.fallback_secondary_color or "#FFFFFF",
		"accent_text_color": settings.fallback_accent_text_color or "#FFFFFF",
		"logo": None,
		"favicon": None,
	}


def _resolve_brand(requested_key: str | None):
	"""
	Resolution order:
	1. Explicit ?brand= query param / function arg
	2. vbl_brand cookie from a previous visit
	3. The Brand Login Settings record marked is_default=1
	4. Hardcoded Vodafone fallback (from Global Settings, or hardcoded red/white)
	"""
	candidates = []
	if requested_key:
		candidates.append(requested_key)

	cookie_key = frappe.request.cookies.get(COOKIE_NAME) if frappe.request else None
	if cookie_key:
		candidates.append(cookie_key)

	for key in candidates:
		key = frappe.utils.strip_html(key or "").strip().lower()
		if not key:
			continue
		brand = frappe.db.get_value(
			"Brand Login Settings",
			{"brand_key": key, "enabled": 1},
			BRAND_FIELDS,
			as_dict=True,
		)
		if brand:
			return brand, key

	default_brand = frappe.db.get_value(
		"Brand Login Settings",
		{"is_default": 1, "enabled": 1},
		BRAND_FIELDS,
		as_dict=True,
	)
	if default_brand:
		return default_brand, default_brand.brand_key

	fallback = _default_brand_dict()
	return fallback, fallback["brand_key"]


@frappe.whitelist(allow_guest=True)
def get_brand_context(brand: str | None = None):
	"""Returns the resolved brand + global footer/switcher settings, and
	(if a brand was explicitly requested) persists the choice as a cookie
	so it survives the redirect chain across login -> update-password ->
	message pages."""
	resolved, resolved_key = _resolve_brand(brand)

	settings = frappe.get_cached_doc("Brand Login Global Settings")

	if brand:
		set_brand_preference(resolved_key)

	return {
		"brand_key": resolved_key,
		"business_name": resolved.get("business_name"),
		"tagline": resolved.get("tagline"),
		"primary_color": resolved.get("primary_color") or "#E60000",
		"secondary_color": resolved.get("secondary_color") or "#FFFFFF",
		"accent_text_color": resolved.get("accent_text_color") or "#FFFFFF",
		"logo": _file_url(resolved.get("logo")),
		"favicon": _file_url(resolved.get("favicon")),
		"show_business_switcher": bool(settings.show_business_switcher),
		"footer_text": settings.footer_text,
		"footer_logo": _file_url(settings.footer_logo),
	}


@frappe.whitelist(allow_guest=True)
def list_brands():
	"""Powers the 'select your business' dropdown on the login page."""
	return frappe.get_all(
		"Brand Login Settings",
		filters={"enabled": 1, "show_in_switcher": 1},
		fields=["brand_key", "business_name", "logo"],
		order_by="sort_order asc, business_name asc",
	)


@frappe.whitelist(allow_guest=True)
def set_brand_preference(brand_key: str):
	"""Explicitly sets the vbl_brand cookie, e.g. when the switcher
	dropdown changes. Only ever stores a brand_key string - no PII."""
	brand_key = frappe.utils.strip_html(brand_key or "").strip().lower()
	if not brand_key:
		return

	settings = frappe.get_cached_doc("Brand Login Global Settings")
	expiry_days = settings.cookie_expiry_days or 30

	frappe.local.cookie_manager.set_cookie(
		COOKIE_NAME,
		brand_key,
		expires=frappe.utils.add_days(frappe.utils.now_datetime(), expiry_days),
	)

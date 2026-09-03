# Copyright (c) 2026, Pranav Dixit / ERPion Technologies LLP
# License: MIT. See license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document


class BrandLoginSettings(Document):
	def validate(self):
		self.slugify_brand_key()
		self.ensure_single_default()

	def slugify_brand_key(self):
		if not self.brand_key:
			source = self.business_name or ""
			self.brand_key = source
		slug = self.brand_key.strip().lower()
		slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
		if not slug:
			frappe.throw(_("Brand Key could not be derived - please set it explicitly."))
		self.brand_key = slug

	def ensure_single_default(self):
		if not self.is_default:
			return
		other_default = frappe.db.exists(
			"Brand Login Settings",
			{"is_default": 1, "name": ["!=", self.name or ""]},
		)
		if other_default:
			frappe.throw(
				_(
					"{0} is already marked as the default brand. "
					"Only one Brand Login Settings record can be the default."
				).format(frappe.bold(other_default))
			)


def create_stub_for_company(doc, method=None):
	"""
	doc_events hook: Company -> after_insert

	Auto-creates a disabled Brand Login Settings stub for every new
	Company, pre-filled from the Company master itself (name + logo),
	so brand data is always sourced from the Company master first.
	An admin only needs to open the stub, set the brand colors and
	tick "Enabled" (and "Show In Business Switcher" if desired).
	"""
	if frappe.db.exists("Brand Login Settings", {"company": doc.name}):
		return

	stub = frappe.new_doc("Brand Login Settings")
	stub.company = doc.name
	stub.business_name = doc.company_name or doc.name
	stub.brand_key = doc.name
	stub.logo = getattr(doc, "company_logo", None)
	stub.enabled = 0  # left disabled until an admin sets the colors and confirms
	stub.show_in_switcher = 0
	stub.primary_color = "#E60000"
	stub.secondary_color = "#FFFFFF"
	stub.accent_text_color = "#FFFFFF"
	stub.insert(ignore_permissions=True)

app_name = "vodafone_brand_login"
app_title = "Vodafone Brand Login"
app_publisher = "Pranav Dixit / ERPion Technologies LLP"
app_description = (
    "Whitelabel theming for ERPNext/Frappe login, signup, password-reset, "
    "message and error pages. Brand colors, logo and business name are "
    "driven by Company-linked Brand Login Settings records, with a "
    "business switcher for multi-company sites. Does not modify core "
    "authentication logic."
)
app_email = "pranav@erpion.in"
app_license = "MIT"
app_icon = "octicon octicon-lock"
app_color = "#E60000"

# Required apps
# --------------
required_apps = ["frappe"]

# Includes in <head>
# ------------------
# These load on every WEBSITE (www/portal) page — i.e. exactly the
# pre-login / auth pages this app themes: /login, /signup,
# /update-password, /message, /404, /429, etc. They are intentionally
# NOT added to app_include_css / app_include_js, which would affect the
# logged-in Desk UI — this app only touches the public-facing auth pages.
web_include_css = "/assets/vodafone_brand_login/css/brand_login.css"
web_include_js = "/assets/vodafone_brand_login/js/brand_login.js"

# Website route rules
# --------------------
# Lets a business-specific login link be shared as either
# /login?brand=<brand_key>  or the friendlier  /b/<brand_key>
# which internally redirects to a themed /login.
website_route_rules = [
    {"from_route": "/b/<brand_key>", "to_route": "brand_redirect"},
]

# Installation
# ------------
after_install = "vodafone_brand_login.install.after_install"

# Doc Events
# ----------
# Auto-create a disabled "stub" Brand Login Settings record whenever a
# new Company master is created, pre-filled with that Company's name
# and logo, so brand data is always sourced from the Company master
# first and only needs color/enable adjustments by an admin.
doc_events = {
    "Company": {
        "after_insert": "vodafone_brand_login.brand_login.doctype.brand_login_settings.brand_login_settings.create_stub_for_company",
    }
}

# Fixtures
# --------
fixtures = []

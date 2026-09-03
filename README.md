# Vodafone Brand Login

Whitelabel theming for the ERPNext / Frappe **login, signup, password-reset,
message and error pages** — for Frappe **version-15**.

Every business Vodafone brings onto this ERPNext instance gets its own
branded login experience (logo, colors, business name), while every
business still shares the exact same underlying authentication logic
(password login, "Login with Email Link", social logins, 2FA, forgot/
reset password). **This app never modifies core auth code** — it only
reads brand data and re-skins the existing pages via CSS + JS, injected
through Frappe's own `web_include_css` / `web_include_js` hooks.

## How it works

1. Two new doctypes:
   - **Brand Login Settings** — one record per business. Holds
     `brand_key` (URL slug), `business_name`, an optional link to that
     business's **Company** master, `primary_color` / `secondary_color`
     / `accent_text_color`, `logo`, `favicon`, and an `is_default` flag
     for the Vodafone fallback brand.
   - **Brand Login Global Settings** (single) — the co-brand footer
     text/logo, whether the business switcher is shown, how long a
     selection is remembered, and the ultimate hard-coded fallback
     (Vodafone red `#E60000` / white).
2. A new **Company** record automatically gets a disabled Brand Login
   Settings *stub*, pre-filled with that company's name and logo — so
   brand data is always sourced from the Company master first. An
   admin just opens the stub, sets the colors, and ticks **Enabled**.
3. On `/login`, `/signup`, `/update-password` and `/message`, a small
   JS file calls a guest-accessible API to resolve which brand to show
   (explicit `?brand=` link → remembered cookie → the `is_default`
   record → hard-coded Vodafone fallback), then injects that brand's
   logo/name/colors into the existing page — without replacing or
   rewriting Frappe's own templates or auth JS.
4. A lightweight **business switcher** dropdown appears on `/login`
   when more than one business is configured, letting a visitor pick
   which company's branding to view. Selecting one just re-themes the
   page and sets a cookie — it has **no effect on actual login
   permissions**, which remain governed entirely by Frappe's normal
   User/Company setup.
5. Each business can also be given a direct shareable link:
   `https://<site>/login?brand=<brand_key>` or the shorter
   `https://<site>/b/<brand_key>`.

## Repository layout

```
vodafone_brand_login/
├── pyproject.toml, requirements.txt, license.txt
└── vodafone_brand_login/
    ├── hooks.py                # app config, web_include_css/js, doc_events, after_install
    ├── install.py              # after_install: global settings + default Vodafone brand
    ├── api.py                  # 3 guest-accessible whitelisted methods
    ├── modules.txt / patches.txt
    ├── patches/
    │   └── create_brand_for_existing_companies.py
    ├── brand_login/doctype/
    │   ├── brand_login_settings/          # per-business brand record
    │   └── brand_login_global_settings/   # site-wide footer/switcher config
    ├── www/
    │   └── brand_redirect.py              # /b/<brand_key> -> /login?brand=<key>
    └── public/
        ├── css/brand_login.css
        └── js/brand_login.js
```

## Installing on a local bench (development / testing)

```bash
# 1. From your bench directory, fetch the app
#    (use a local path while testing, or your git remote once pushed)
bench get-app vodafone_brand_login /path/to/vodafone_brand_login
# or, once pushed to git:
# bench get-app https://github.com/ERPION2025/ERPNext-V15-Brand-Login-Page.git --branch main

# 2. Install it on the target site (must already have erpnext installed)
bench --site your-site.local install-app vodafone_brand_login

# 3. Build assets and migrate
bench build --app vodafone_brand_login
bench --site your-site.local migrate

# 4. Start bench and visit /login
bench start
```

`install-app` runs `after_install`, which:
- creates the **Brand Login Global Settings** singleton with sensible
  defaults (Vodafone red/white, footer text, switcher on)
- creates the default `vodafone` **Brand Login Settings** record
  (`is_default = 1`, not shown in the switcher — it's the fallback)
- back-fills a disabled brand stub for any **Company** records that
  already existed on the site before this app was installed

## Deploying on Frappe Cloud

Frappe Cloud installs custom apps from a git repository, not from a
local folder, so:

1. **Push this app to a GitHub repository.** This repo is already at
   [ERPION2025/ERPNext-V15-Brand-Login-Page](https://github.com/ERPION2025/ERPNext-V15-Brand-Login-Page)
   on the `main` branch — Frappe Cloud doesn't require a specific
   branch name, you pick the branch explicitly in the dashboard, so
   `main` is fine as-is.
   ```bash
   git add .
   git commit -m "Vodafone Brand Login v15 - ready for Frappe Cloud"
   git push origin main
   ```
2. In the **Frappe Cloud dashboard** → your Bench → **Apps** → **Install
   App**, paste the repository URL and select the `main` branch.
   Frappe Cloud will ask to authorize access if the repo is private.
3. Once the app is attached to the Bench, deploy the Bench (this runs
   the equivalent of `get-app` + a fresh build on Frappe Cloud's
   infrastructure).
4. On each **Site** using that Bench, go to **Site → Apps → Install**
   and install `Vodafone Brand Login`. This triggers `after_install`
   exactly as in local dev.
5. If the app is added to a Bench that's already running sites with
   existing Company records, also run **Site → Console/Bench →
   migrate** (or trigger it from the dashboard) so the safety-net patch
   (`create_brand_for_existing_companies`) back-fills brand stubs for
   any Company created before install.

## Post-install configuration

1. Open **Brand Login Global Settings** (Setup/Search) and set the
   Vodafone co-brand footer text/logo if you want something other than
   the default *"Powered by Vodafone X ERPNext"*.
2. Open the **Brand Login Settings** list. Every Company on the site
   already has a disabled stub with its name/logo pre-filled from the
   Company master. For each business:
   - Set `Primary Color`, `Secondary Color`, `Accent Text Color`.
   - Confirm/adjust `Brand Key` (this becomes the URL slug).
   - Tick **Enabled**, and **Show In Business Switcher** if it should
     appear in the public dropdown.
3. Test at `https://<site>/login?brand=<brand_key>` or share
   `https://<site>/b/<brand_key>`.
4. The default, unbranded `/login` shows Vodafone red/white with the
   business switcher (if more than one enabled business exists).

## What this app deliberately does **not** touch

- No changes to `frappe.www.login`, `login.js`, 2FA, social login, or
  the "Login with Email Link" backend logic — all of that is 100%
  stock Frappe.
- No changes to Desk / the logged-in workspace UI — only the public
  pre-login pages are themed (`web_include_css/js`, not
  `app_include_css/js`).
- No permission or company-scoping changes — the business switcher is
  purely cosmetic. A user's actual login and Company access are still
  governed entirely by their User/Company/Role setup.

## Known limitation — generic 404 / 429 / error pages

Frappe's error pages don't have a fixed URL (the browser shows
whatever bad path was requested), so they can't be targeted by
pathname the way `/login` or `/signup` can. `brand_login.js` instead
uses a best-effort heuristic (`looksLikeErrorPage()` in
`public/js/brand_login.js`) to detect that it's on an error page, and
only re-themes it (colors + a small logo, no switcher) if a business
was already selected earlier in the session. If your Frappe version's
error-page markup doesn't match the selectors in that function,
open `public/js/brand_login.js` and adjust the `looksLikeErrorPage`
selector list to match — everything else in the app is unaffected.

## Uninstalling

```bash
bench --site your-site.local uninstall-app vodafone_brand_login
```
This removes both doctypes and all Brand Login Settings records. The
login/signup/reset-password pages immediately revert to stock Frappe
styling since no core template was ever modified.

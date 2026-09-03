This is a complete, installable bench app — vodafone_brand_login, targeting Frappe version-15. Quick orientation:

Core design: it never overrides Frappe's actual login/signup/reset-password templates or JS — instead it injects CSS + JS via the standard web_include_css/web_include_js hooks to re-skin the existing pages. That's what keeps every auth mechanism (password, email-link login, 2FA, social login) exactly as-is while still reaching every page in the flow.

What's in it:

Brand Login Settings doctype — one record per business (colors, logo, business name, optional Company link, brand_key for shareable URLs)
Brand Login Global Settings — the Vodafone co-brand footer, switcher toggle, cookie duration, and ultimate fallback colors
A Company: after_insert hook that auto-creates a disabled brand stub the moment any new Company master is added, pre-filled from that Company's name/logo
api.py — 3 guest-accessible endpoints that resolve brand (explicit link → cookie → default → hardcoded Vodafone red/white) and drive the business switcher
brand_login.css / brand_login.js — the actual theming + the injected logo/name/switcher/footer, with a MutationObserver so it survives the 2FA/email-link DOM swaps
install.py + a post_model_sync patch — sets sane defaults and back-fills brand stubs, both on fresh install and when added to a bench that already has Companies
Full README with local bench get-app/install-app steps and the Frappe Cloud git-repo deployment flow

One honest caveat (documented in the README and in the JS comments): Frappe's 404/429 error pages don't have a fixed URL, so they're detected heuristically rather than by path — I've flagged exactly which selectors to adjust if your instance's error markup differs, since I can't test this against a live v15 bench from here.

Every JSON schema and Python file passed syntax validation; the JS passed a Node syntax check. Worth a real bench install-app test-run on a dev site before pointing it at Vodafone's actual sites.

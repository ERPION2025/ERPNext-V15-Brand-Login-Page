/*
 * Vodafone Brand Login - runtime theming script
 * Loaded on every website (www) page via the web_include_js hook in
 * hooks.py. Deliberately does NOT touch any authentication logic -
 * it only reads brand data (colors/name/logo) and redecorates the
 * existing Frappe login/signup/reset-password/message DOM, and
 * lightly touches error pages when a brand cookie is already set.
 *
 * KNOWN LIMITATION: Frappe's 404/429/error pages don't expose a
 * stable URL (the browser shows whatever bad path was requested), so
 * they can't be targeted by pathname. This script instead detects
 * "is this a Frappe error page" heuristically (see looksLikeErrorPage
 * below) and, when a business has already been selected earlier in
 * the session (vbl_brand cookie present), applies a light-touch theme
 * (colors + small logo) rather than the full header/switcher. If your
 * Frappe version's error markup differs, adjust the selectors in
 * looksLikeErrorPage().
 */
(function () {
	"use strict";

	var COOKIE_NAME = "vbl_brand";
	var CORE_PAGES = ["/login", "/signup", "/update-password", "/message"];

	function currentPath() {
		return window.location.pathname.replace(/\/+$/, "") || "/";
	}

	function isCorePage() {
		return CORE_PAGES.indexOf(currentPath()) !== -1;
	}

	function hasBrandCookie() {
		return document.cookie.split("; ").some(function (c) {
			return c.indexOf(COOKIE_NAME + "=") === 0;
		});
	}

	function looksLikeErrorPage() {
		return !!document.querySelector(
			[
				".error-page",
				"#error-page",
				".page-404",
				".http-error",
				"[data-http-status]",
				".not-found",
			].join(",")
		);
	}

	function getQueryParam(name) {
		return new URLSearchParams(window.location.search).get(name);
	}

	function callMethod(method, args) {
		var qs = args ? "?" + new URLSearchParams(args).toString() : "";
		return fetch("/api/method/" + method + qs, {
			headers: { "X-Requested-With": "XMLHttpRequest" },
			credentials: "same-origin",
		})
			.then(function (r) {
				return r.json();
			})
			.then(function (data) {
				return data && data.message;
			})
			.catch(function () {
				return null;
			});
	}

	function applyCssVars(ctx) {
		var root = document.documentElement;
		root.style.setProperty("--vbl-primary", ctx.primary_color || "#E60000");
		root.style.setProperty("--vbl-secondary", ctx.secondary_color || "#FFFFFF");
		root.style.setProperty("--vbl-accent-text", ctx.accent_text_color || "#FFFFFF");
	}

	function applyFavicon(ctx) {
		if (!ctx.favicon) return;
		var link = document.querySelector("link[rel~='icon']");
		if (!link) {
			link = document.createElement("link");
			link.rel = "icon";
			document.head.appendChild(link);
		}
		link.href = ctx.favicon;
	}

	function applyTitle(ctx) {
		if (!ctx.business_name) return;
		document.title = document.title.replace(/^.*? - /, ctx.business_name + " - ");
	}

	function findCardContainer() {
		var selectors = [
			".page-card-body",
			".page-card",
			".for-login",
			".signup-form-wrapper",
			".update-password-form-wrapper",
			"#page-message .container",
			"main .container",
		];
		for (var i = 0; i < selectors.length; i++) {
			var el = document.querySelector(selectors[i]);
			if (el) return el;
		}
		return document.body;
	}

	function buildHeader(ctx) {
		var wrap = document.createElement("div");
		wrap.className = "vbl-header";

		if (ctx.logo) {
			var img = document.createElement("img");
			img.className = "vbl-logo";
			img.src = ctx.logo;
			img.alt = ctx.business_name || "";
			wrap.appendChild(img);
		}

		var name = document.createElement("div");
		name.className = "vbl-business-name";
		name.textContent = ctx.business_name || "Vodafone";
		wrap.appendChild(name);

		if (ctx.tagline) {
			var tagline = document.createElement("div");
			tagline.className = "vbl-tagline";
			tagline.textContent = ctx.tagline;
			wrap.appendChild(tagline);
		}

		return wrap;
	}

	function buildFooter(ctx) {
		var wrap = document.createElement("div");
		wrap.className = "vbl-footer";

		var text = document.createElement("span");
		text.textContent = ctx.footer_text || "Powered by Vodafone X ERPNext";
		wrap.appendChild(text);

		if (ctx.footer_logo) {
			var img = document.createElement("img");
			img.src = ctx.footer_logo;
			img.alt = "Vodafone";
			wrap.appendChild(img);
		}

		return wrap;
	}

	function buildSwitcher(ctx, onChange) {
		var wrap = document.createElement("div");
		wrap.className = "vbl-switcher";

		var label = document.createElement("label");
		label.textContent = "Select your business";
		wrap.appendChild(label);

		var select = document.createElement("select");
		var placeholder = document.createElement("option");
		placeholder.value = "";
		placeholder.textContent = "Vodafone (default)";
		select.appendChild(placeholder);
		wrap.appendChild(select);

		callMethod("vodafone_brand_login.api.list_brands").then(function (brands) {
			(brands || []).forEach(function (b) {
				var opt = document.createElement("option");
				opt.value = b.brand_key;
				opt.textContent = b.business_name;
				if (b.brand_key === ctx.brand_key) opt.selected = true;
				select.appendChild(opt);
			});
		});

		select.addEventListener("change", function () {
			onChange(select.value);
		});

		return wrap;
	}

	function injectFull(ctx) {
		if (document.querySelector(".vbl-header")) return; // already injected

		var container = findCardContainer();
		var header = buildHeader(ctx);
		container.insertBefore(header, container.firstChild);

		if (ctx.show_business_switcher && currentPath() === "/login") {
			var switcher = buildSwitcher(ctx, function (brandKey) {
				var url = new URL(window.location.href);
				if (brandKey) {
					url.searchParams.set("brand", brandKey);
				} else {
					url.searchParams.delete("brand");
				}
				window.location.href = url.toString();
			});
			container.insertBefore(switcher, header.nextSibling);
		}

		var footer = buildFooter(ctx);
		(container.parentNode || container).appendChild(footer);
	}

	function injectLight(ctx) {
		if (document.querySelector(".vbl-header")) return;
		var header = buildHeader(ctx);
		document.body.insertBefore(header, document.body.firstChild);
		document.body.setAttribute("data-vbl-error", "1");
	}

	function watchForRerender(ctx, injectFn) {
		// Frappe's 2FA / email-link login states swap DOM content inside
		// the card. If our injected header ever gets wiped out by that,
		// put it back.
		var observer = new MutationObserver(function () {
			if (!document.querySelector(".vbl-header")) {
				injectFn(ctx);
			}
		});
		observer.observe(document.body, { childList: true, subtree: true });
	}

	function init() {
		var brandParam = getQueryParam("brand");
		var core = isCorePage();
		var errorCandidate = !core && hasBrandCookie() && looksLikeErrorPage();

		if (!core && !errorCandidate) {
			return; // ordinary website page, nothing to do
		}

		callMethod("vodafone_brand_login.api.get_brand_context", brandParam ? { brand: brandParam } : null).then(
			function (ctx) {
				if (!ctx) return;

				document.body.setAttribute("data-vbl-active", "1");
				applyCssVars(ctx);
				applyFavicon(ctx);
				applyTitle(ctx);

				if (core) {
					injectFull(ctx);
					watchForRerender(ctx, injectFull);
				} else {
					injectLight(ctx);
				}
			}
		);
	}

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", init);
	} else {
		init();
	}
})();

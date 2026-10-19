/* Shared behaviour for all five designs.
   Reads window.PRODUCTS / window.SITE from products.js.
   You should not need to edit this file. */
(function () {
  "use strict";

  var PLACEHOLDER = "PASTE_CHECKOUT_LINK_HERE";
  var products = window.PRODUCTS || [];
  var site = window.SITE || {};

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function checkoutHref(p) {
    if (!p.checkout || p.checkout === PLACEHOLDER) {
      console.warn("[" + (site.brand || "site") + "] No checkout link set for \"" + p.name + "\". Edit shared/products.js");
      return "#checkout-missing";
    }
    return p.checkout;
  }

  function buyAttrs(p) {
    return 'href="' + esc(checkoutHref(p)) + '" data-buy="' + esc(p.id) + '" rel="noopener"';
  }

  /* ---------- Product cards ---------- */
  function cardHTML(p, i) {
    var was = p.compareAt ? '<s class="pc-was">' + esc(p.compareAt) + "</s>" : "";
    var badge = p.badge ? '<span class="pc-badge">' + esc(p.badge) + "</span>" : "";
    var feats = (p.features || []).map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("");
    return (
      '<article class="pc' + (/popular/i.test(p.badge || "") ? " pc--featured" : (p.badge ? " pc--badged" : "")) + '" data-id="' + esc(p.id) + '" style="--i:' + i + '">' +
        badge +
        '<div class="pc-head">' +
          '<h3 class="pc-name">' + esc(p.name) + "</h3>" +
          '<p class="pc-short">' + esc(p.short) + "</p>" +
        "</div>" +
        '<div class="pc-price"><span class="pc-now">' + esc(p.price) + "</span>" + was + "</div>" +
        '<ul class="pc-features">' + feats + "</ul>" +
        '<p class="pc-access">' + esc(p.access || "") + "</p>" +
        '<div class="pc-actions">' +
          '<a class="btn btn-buy" ' + buyAttrs(p) + ">Buy now</a>" +
          '<button class="btn btn-details" type="button" data-details="' + esc(p.id) + '">What’s inside</button>' +
        "</div>" +
      "</article>"
    );
  }

  function renderProducts() {
    var hosts = document.querySelectorAll("[data-products]");
    Array.prototype.forEach.call(hosts, function (host) {
      host.innerHTML = products.map(cardHTML).join("");
    });
  }

  /* ---------- Detail modal ---------- */
  function ensureModal() {
    if (document.getElementById("product-modal")) return;
    var m = document.createElement("div");
    m.id = "product-modal";
    m.className = "modal";
    m.setAttribute("aria-hidden", "true");
    m.innerHTML =
      '<div class="modal-backdrop" data-close></div>' +
      '<div class="modal-card" role="dialog" aria-modal="true" aria-labelledby="modal-title">' +
        '<button class="modal-x" type="button" data-close aria-label="Close">×</button>' +
        '<div class="modal-body"></div>' +
      "</div>";
    document.body.appendChild(m);
  }

  function modalHTML(p) {
    var feats = (p.features || []).map(function (f) { return "<li>" + esc(f) + "</li>"; }).join("");
    var was = p.compareAt ? '<s class="modal-was">' + esc(p.compareAt) + "</s>" : "";
    return (
      (p.badge ? '<span class="modal-badge">' + esc(p.badge) + "</span>" : "") +
      '<h2 id="modal-title" class="modal-title">' + esc(p.name) + "</h2>" +
      '<p class="modal-short">' + esc(p.short) + "</p>" +
      '<p class="modal-desc">' + esc(p.description) + "</p>" +
      '<ul class="modal-features">' + feats + "</ul>" +
      '<div class="modal-foot">' +
        '<div class="modal-price"><span class="modal-now">' + esc(p.price) + "</span>" + was +
          '<span class="modal-access">' + esc(p.access || "") + "</span></div>" +
        '<a class="btn btn-buy btn-buy--lg" ' + buyAttrs(p) + ">Buy now — go to checkout</a>" +
      "</div>" +
      '<p class="modal-safe">Secure checkout. You will be taken straight to the payment page.</p>'
    );
  }

  var lastFocus = null;
  function openModal(id) {
    var p = products.filter(function (x) { return x.id === id; })[0];
    if (!p) return;
    ensureModal();
    var m = document.getElementById("product-modal");
    m.querySelector(".modal-body").innerHTML = modalHTML(p);
    lastFocus = document.activeElement;
    m.classList.add("is-open");
    m.setAttribute("aria-hidden", "false");
    document.documentElement.classList.add("modal-open");
    var first = m.querySelector(".btn-buy");
    if (first) first.focus();
  }
  function closeModal() {
    var m = document.getElementById("product-modal");
    if (!m) return;
    m.classList.remove("is-open");
    m.setAttribute("aria-hidden", "true");
    document.documentElement.classList.remove("modal-open");
    if (lastFocus && lastFocus.focus) lastFocus.focus();
  }

  /* ---------- Missing-link notice ---------- */
  function showMissingNotice(name) {
    var n = document.getElementById("checkout-missing-notice");
    if (!n) {
      n = document.createElement("div");
      n.id = "checkout-missing-notice";
      n.className = "notice";
      document.body.appendChild(n);
    }
    n.textContent = "Checkout link for “" + name + "” is not set yet. Open shared/products.js and paste your link.";
    n.classList.add("is-on");
    clearTimeout(n._t);
    n._t = setTimeout(function () { n.classList.remove("is-on"); }, 4500);
  }

  /* ---------- Events ---------- */
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-details],[data-close],[data-buy]") : null;
    if (!t) return;
    if (t.hasAttribute("data-details")) { e.preventDefault(); openModal(t.getAttribute("data-details")); return; }
    if (t.hasAttribute("data-close")) { e.preventDefault(); closeModal(); return; }
    if (t.hasAttribute("data-buy") && t.getAttribute("href") === "#checkout-missing") {
      e.preventDefault();
      var p = products.filter(function (x) { return x.id === t.getAttribute("data-buy"); })[0];
      showMissingNotice(p ? p.name : "this product");
    }
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });

  /* ---------- Reveal on scroll ---------- */
  function reveal() {
    var els = document.querySelectorAll("[data-reveal]");
    if (!("IntersectionObserver" in window)) {
      Array.prototype.forEach.call(els, function (el) { el.classList.add("in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.15 });
    Array.prototype.forEach.call(els, function (el) { io.observe(el); });
  }

  /* ---------- Count-up numbers: <span data-count="850" data-suffix="+"> ---------- */
  function countUp() {
    var els = document.querySelectorAll("[data-count]");
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    function run(el) {
      var end = parseFloat(el.getAttribute("data-count"));
      var suf = el.getAttribute("data-suffix") || "";
      var pre = el.getAttribute("data-prefix") || "";
      if (reduce) { el.textContent = pre + end + suf; return; }
      var t0 = null, dur = 1400;
      function step(ts) {
        if (!t0) t0 = ts;
        var k = Math.min(1, (ts - t0) / dur);
        var eased = 1 - Math.pow(1 - k, 3);
        el.textContent = pre + Math.round(end * eased) + suf;
        if (k < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }
    if (!("IntersectionObserver" in window)) { Array.prototype.forEach.call(els, run); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { run(en.target); io.unobserve(en.target); } });
    }, { threshold: 0.4 });
    Array.prototype.forEach.call(els, function (el) { io.observe(el); });
  }

  /* ---------- States + brand fill-ins ---------- */
  function fillSite() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-brand]"), function (el) { el.textContent = site.brand || ""; });
    Array.prototype.forEach.call(document.querySelectorAll("[data-states]"), function (el) {
      el.innerHTML = (site.states || []).map(function (s) { return "<span>" + esc(s) + "</span>"; }).join("");
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-codenote]"), function (el) { el.textContent = site.codeNote || ""; });
    Array.prototype.forEach.call(document.querySelectorAll("[data-year]"), function (el) { el.textContent = new Date().getFullYear(); });
    Array.prototype.forEach.call(document.querySelectorAll("[data-email]"), function (el) {
      el.textContent = site.supportEmail || ""; el.setAttribute("href", "mailto:" + (site.supportEmail || ""));
    });
    // Featured product shortcuts: <a data-buy-featured> jumps to the badge "Most popular" product's checkout
    var feat = products.filter(function (p) { return /popular/i.test(p.badge || ""); })[0] || products[0];
    if (feat) {
      Array.prototype.forEach.call(document.querySelectorAll("[data-buy-featured]"), function (el) {
        el.setAttribute("href", checkoutHref(feat)); el.setAttribute("data-buy", feat.id);
      });
      Array.prototype.forEach.call(document.querySelectorAll("[data-featured-name]"), function (el) { el.textContent = feat.name; });
      Array.prototype.forEach.call(document.querySelectorAll("[data-featured-price]"), function (el) { el.textContent = feat.price; });
    }
  }

  /* ---------- FAQ accordions: <details> get smooth open ---------- */
  function faq() {
    Array.prototype.forEach.call(document.querySelectorAll(".faq details"), function (d) {
      d.addEventListener("toggle", function () {
        if (d.open) {
          Array.prototype.forEach.call(d.parentNode.querySelectorAll("details"), function (o) { if (o !== d) o.open = false; });
        }
      });
    });
  }

  function init() {
    renderProducts();
    ensureModal();
    fillSite();
    reveal();
    countUp();
    faq();
    document.documentElement.classList.add("js");
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();

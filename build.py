#!/usr/bin/env python3
"""Build passyourvirginiacontractorexam.com.

  python3 build.py

Pages:
  /                               every license, grouped (contractor, business, trades, officials, codes)
  /<license>/                     one page per license class with all its packages, a comparison table and an FAQ
  /<license>/<package>/           one page per product, Buy now goes straight to checkout
  /faq/  /blog/  /search/  /admin/  robots.txt  llms.txt  agents.md  sitemap.xml  index.md copies

Products come from shared/catalog.js + store/products-full.json (written by the dashboard sync or by
tools/sync_shopify.py). Classes and package types are worked out from the titles by tools/vaclass.py,
and the license copy lives in tools/vacopy.py. Previously generated folders are removed first.
"""
import json, os, re, sys, shutil, html, datetime, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import blogkit, vaclass, vacopy

tpl = open(os.path.join(ROOT, "store", "template.html"), encoding="utf-8").read()
ptpl = open(os.path.join(ROOT, "store", "product.html"), encoding="utf-8").read()
FULL = json.load(open(os.path.join(ROOT, "store", "products-full.json"), encoding="utf-8"))
cat_js = open(os.path.join(ROOT, "shared", "catalog.js"), encoding="utf-8").read()
_end = cat_js.index(";\nwindow.CATALOG_STATES") if ";\nwindow.CATALOG_STATES" in cat_js else cat_js.rindex(";")
CATALOG = json.loads(cat_js[cat_js.index("window.CATALOG=") + len("window.CATALOG="):_end])
CFG = json.load(open(os.path.join(ROOT, "site-config.json"), encoding="utf-8"))
SITE = CFG["siteUrl"].rstrip("/") + "/" if CFG.get("siteUrl") else None
BRAND = CFG.get("brand", "1 Exam Prep")
FUL = CFG.get("fulfillment") or {"name": "1 Exam Prep", "url": CFG.get("storeUrl", "https://1examprep.com"), "note": ""}
STORE = CFG.get("storeUrl", "https://1examprep.com").rstrip("/")
WM = CFG.get("wordmark") or [BRAND, "", ""]
_nb = lambda x: html.escape(x).replace(" ", "&nbsp;")
WORDMARK_TEXT = "%s<span>%s</span>%s" % (_nb(WM[0]), _nb(WM[1]), _nb(WM[2])) if WM[1] else html.escape(WM[0])
LOGO_NAV = CFG.get("logoNav") if CFG.get("logoNav") and os.path.exists(os.path.join(ROOT, CFG.get("logoNav"))) else None
HAS_PNG_ICONS = os.path.exists(os.path.join(ROOT, "shared", "favicon.png"))
TODAY = datetime.date.today().isoformat()
LAUNCH = CFG.get("launched", TODAY)

# ---------- products, classes ----------
PRODUCTS = vaclass.assign([p for p in CATALOG if p.get("variants")])
GROUP_NAME = {g: n for g, n, _ in vaclass.GROUPS}
GROUP_BLURB = {g: b for g, _, b in vaclass.GROUPS}
CLASSES = {}  # slug -> dict
for p in PRODUCTS:
    c = CLASSES.setdefault(p["cls"], {"slug": p["cls"], "name": p["clsName"], "group": p["group"], "products": []})
    c["products"].append(p)
for c in CLASSES.values():
    c["products"].sort(key=lambda p: (p["region"] != "Virginia", p["rank"], float(p["price"]), p["title"]))
    c["lo"] = min(float(p["price"]) for p in c["products"]); c["hi"] = max(float(p["price"]) for p in c["products"])
ORDER = [c[0] for c in vaclass.CLASSES] + [vaclass.OTHER[0]]
def classes_in(group): return [CLASSES[s] for s in ORDER if s in CLASSES and CLASSES[s]["group"] == group]
UNCLASSIFIED = [p["title"] for p in PRODUCTS if p["cls"] == "other" or p["type"] == "other"]

# ---------- helpers ----------
def wordmark(rel):
    if LOGO_NAV: return '<img class="brand-img" src="%s%s" alt="%s" width="172" height="48" decoding="async">' % (rel, LOGO_NAV, html.escape(BRAND))
    return WORDMARK_TEXT
def brand_tokens(out, rel=None):
    if rel is None:
        m = re.search(r'href="((?:\.\./)*)shared/base\.css"', out); rel = m.group(1) if m else ""
    return (out.replace("{{WORDMARK}}", wordmark(rel)).replace("{{BRAND}}", html.escape(BRAND)).replace("{{FULFILL_NAME}}", html.escape(FUL["name"]))
               .replace("{{FULFILL_URL}}", html.escape(FUL["url"])).replace("{{PHONE}}", html.escape(CFG["phone"])).replace("{{PHONE_TEL}}", CFG["phoneTel"]))
def nice_day(d):
    try: return datetime.date.fromisoformat(d[:10]).strftime("%B %-d, %Y")
    except Exception: return d
def money(v):
    v = float(v); return ("$%s" % format(int(v), ",")) if v == int(v) else ("$%s" % format(v, ",.2f"))
def esc(s): return html.escape(str(s))
def trim_desc(d, n=158):
    d = re.sub(r"\s+", " ", d).strip()
    if len(d) <= n: return d
    cut = d[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + ("" if cut.endswith(".") else ".")
def fit_title(*options, lo=30, hi=60):
    for o in options:
        o = re.sub(r"\s+", " ", o).strip()
        if lo <= len(o) <= hi: return o
    o = re.sub(r"\s+", " ", options[-1]).strip()
    return o[:hi].rsplit(" ", 1)[0] if len(o) > hi else o
def anchor_ids(out):
    out = brand_tokens(out)
    seen = set(re.findall(r'\sid="([^"]+)"', out))
    def rep(m):
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        if re.search(r'\sid=', attrs): return m.group(0)
        base = re.sub(r"[^a-z0-9]+", "-", html.unescape(re.sub(r"<[^>]+>", "", inner)).lower()).strip("-")[:60] or "section"
        i, hid = 1, base
        while hid in seen: i += 1; hid = "%s-%d" % (base, i)
        seen.add(hid)
        return '<%s%s id="%s">%s</%s>' % (tag, attrs, hid, inner, tag)
    return re.sub(r"<(h[23])(\s[^>]*)?>(.*?)</\1>", rep, out, flags=re.S)
def absurl(path): return (SITE + path) if SITE else "/" + path
def ld(obj): return '<script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)
def org_ld():
    o = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "legalName": CFG.get("legalName", BRAND), "url": SITE or STORE,
         "logo": CFG.get("logo"), "telephone": CFG.get("phoneTel"), "email": CFG.get("email"), "sameAs": [v for v in CFG.get("social", {}).values() if v],
         "parentOrganization": {"@type": "Organization", "name": FUL["name"], "url": FUL["url"]} if FUL["name"] != BRAND else None,
         "areaServed": {"@type": "State", "name": "Virginia"},
         "contactPoint": [{"@type": "ContactPoint", "telephone": CFG.get("phoneTel"), "email": CFG.get("email"), "contactType": "sales", "areaServed": "US-VA", "availableLanguage": "English"}]}
    return {k: v for k, v in o.items() if v}
def publisher_ld():
    o = {"@type": "Organization", "name": BRAND, "url": SITE or STORE, "logo": {"@type": "ImageObject", "url": CFG.get("logo")} if CFG.get("logo") else None,
         "telephone": CFG.get("phoneTel"), "email": CFG.get("email")}
    return {k: v for k, v in o.items() if v}
def website_ld():
    return {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE or "/", "publisher": publisher_ld(),
            "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": absurl("search/?q={search_term_string}")}, "query-input": "required name=search_term_string"}}
def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absurl(pth)} for i, (n, pth) in enumerate(items)]}
def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in pairs]}

def head_extra(path, title, desc, image, rel, noindex=False, extra_ld=(), page_type="WebPage", about="Virginia contractor, tradesman and code official licensing exams"):
    desc = trim_desc(desc)
    url = absurl(path) if SITE else None
    h = ['<meta name="robots" content="%s">' % ("noindex, nofollow" if noindex else "index, follow, max-image-preview:large")]
    if url: h.append('<meta property="og:url" content="%s">' % esc(url))
    if url and not noindex: h.append('<link rel="alternate" type="text/markdown" title="Markdown version for AI assistants" href="%s">' % esc(url + "index.md"))
    h += ['<meta property="og:site_name" content="%s">' % esc(BRAND), '<meta property="og:locale" content="en_US">', '<meta name="twitter:card" content="summary_large_image">',
          '<meta name="twitter:title" content="%s">' % esc(title), '<meta name="twitter:description" content="%s">' % esc(desc)]
    if image: h.append('<meta name="twitter:image" content="%s">' % esc(image))
    if CFG.get("social", {}).get("twitter"): h.append('<meta name="twitter:site" content="@%s">' % CFG["social"]["twitter"].rstrip("/").split("/")[-1])
    h.append('<meta name="theme-color" content="#1b1f3b">')
    h.append('<script>window.SITE=%s;</script>' % json.dumps({"brand": BRAND, "storeUrl": STORE, "fulfillment": FUL["name"]}))
    if not LOGO_NAV: h.append('<style>.nav .brand{font-size:1.05rem;line-height:1.05;max-width:46vw}@media (max-width:720px){.nav .brand{font-size:.9rem}}</style>')
    h.append('<link rel="icon" href="%sshared/%s">' % (rel, "favicon.png\" type=\"image/png\" sizes=\"64x64" if HAS_PNG_ICONS else "favicon.svg\" type=\"image/svg+xml"))
    h.append('<link rel="apple-touch-icon" href="%sshared/apple-touch-icon.png">' % rel); h.append('<link rel="manifest" href="%smanifest.webmanifest">' % rel)
    if CFG.get("googleSiteVerification"): h.append('<meta name="google-site-verification" content="%s">' % esc(CFG["googleSiteVerification"]))
    if CFG.get("gtagId"): h.append('<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","%s",{"send_page_view":true});</script>' % (CFG["gtagId"], CFG["gtagId"]))
    if CFG.get("gtmId"): h.append("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','%s');</script>" % CFG["gtmId"])
    if CFG.get("metaPixelId"): h.append("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','%s');fbq('track','PageView');</script>" % CFG["metaPixelId"])
    if CFG.get("dashboardUrl") and CFG.get("siteKey"): h.append('<script>window.__dashCustom=true;</script><script src="%s/t.js" data-site="%s" defer></script>' % (esc(CFG["dashboardUrl"].rstrip("/")), esc(CFG["siteKey"])))
    for o in extra_ld: h.append(ld(o).rstrip())
    if url and not noindex and page_type:
        h.append(ld({"@context": "https://schema.org", "@type": page_type, "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en-US", "datePublished": LAUNCH, "dateModified": TODAY,
                     "isPartOf": {"@type": "WebSite", "url": SITE, "name": BRAND}, "publisher": publisher_ld(), "about": {"@type": "Thing", "name": about}}).rstrip())
    return "\n".join(h) + "\n"

ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'
ICON_SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
def nav_tools(cta_html):
    return ('<div class="nav-tools"><a class="nav-phone" href="tel:%s" aria-label="Call %s">%s<span>%s</span></a>'
            '<button type="button" class="nav-search" data-sopen aria-label="Search the site">%s</button>%s</div>' % (CFG["phoneTel"], CFG["phone"], ICON_PHONE, esc(CFG["phone"]), ICON_SEARCH, cta_html))
POPULAR = ["commercial-building", "residential-building", "home-improvement", "journeyman-electrician", "master-plumber", "commercial-building-inspector"]
def footer(rel):
    home = rel or "./"
    soc = "".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (esc(u), k.capitalize()) for k, u in CFG.get("social", {}).items() if u)
    pop = "".join('<li><a href="%s%s/">%s</a></li>' % (rel, s, esc(CLASSES[s]["name"])) for s in POPULAR if s in CLASSES)
    return ('<footer class="site-footer"><div class="wrap"><div class="cols">'
            '<div><a class="brand" href="%s">{{WORDMARK}}</a><p>%s</p><p class="contact"><a href="tel:%s">%s</a><a href="mailto:%s">%s</a></p></div>'
            '<nav aria-label="Popular licenses"><h2>Popular licenses</h2><ul>%s<li><a href="%s#contractor">All %d licenses</a></li></ul></nav>'
            '<nav aria-label="Shop"><h2>Shop</h2><ul><li><a href="%s#contractor">Contractor classes</a></li><li><a href="%s#trades">Tradesman licenses</a></li><li><a href="%s#officials">Inspectors and plans examiners</a></li><li><a href="%sfaq/">FAQ</a></li><li><a href="%sblog/">Blog</a></li><li><a href="%ssearch/">Search</a></li></ul></nav>'
            '<nav aria-label="Follow"><h2>Follow</h2><ul>%s</ul></nav></div>'
            '<p class="fine"><strong>%s</strong> &copy; <span data-year>%s</span> &middot; %s Prices and availability come from the fulfillment store and were last checked <time datetime="%s">%s</time>; the price at checkout is the one that applies. Not affiliated with DPOR, the Board for Contractors, DHCD, ICC, NASCLA or PSI. Buying study material does not grant exam eligibility or a license.</p></div></footer>'
            % (home, esc(CFG.get("tagline", "")), CFG["phoneTel"], esc(CFG["phone"]), CFG["email"], CFG["email"], pop, home, len(CLASSES), home, home, home, rel, rel, rel, soc,
               esc(BRAND), TODAY[:4], esc(FUL.get("note") or ("Orders are processed and shipped by %s, our fulfillment center." % FUL["name"])), TODAY, nice_day(TODAY)))
def takeaways_html(items, title="Key takeaways", hid="key-takeaways"):
    items = [i for i in items if i][:5]
    if not items: return ""
    return ('<aside class="takeaways" aria-labelledby="%s"><h2 id="%s">%s</h2><ul>%s</ul><p class="upd">Updated <time datetime="%s">%s</time> · prices checked against the %s store</p></aside>'
            % (hid, hid, title, "".join("<li>%s</li>" % esc(i) for i in items), TODAY, nice_day(TODAY), esc(FUL["name"])))
def faq_html(pairs, open_first=True):
    return '<div class="faq">%s</div>' % "".join('<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if open_first and i == 0 else "", esc(q), a if "<a " in a else esc(a)) for i, (q, a) in enumerate(pairs))
def sources_html(group, extra=()):
    items = list(vacopy.SOURCES.get(group, vacopy.SOURCES["contractor"])) + list(extra)
    return ('<section class="wrap sources" aria-labelledby="h-sources"><h2 id="h-sources">Sources</h2><ul>%s</ul><p class="upd">Licensing facts checked against these pages; last updated <time datetime="%s">%s</time>. Rules change, so confirm with the board before you apply.</p></section>'
            % ("".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (esc(u), esc(n)) for n, u in items), TODAY, nice_day(TODAY)))
def cart(vid): return "%s/cart/%s:1" % (STORE, vid)
def region_note(p): return "" if p["region"] == "Virginia" else (" (%s edition)" % p["region"] if p["region"] != "Nationwide" else " (any state)")

def card_html(p, rel):
    c, n = float(p.get("compareAt") or 0), float(p["price"])
    save = ('<s class="pc-was">%s</s><span class="pc-save">Save %d%%</span>' % (money(c), round((c - n) / c * 100))) if c > n else ""
    more = ('<small style="color:var(--muted)"> to %s</small>' % money(p["maxPrice"])) if p.get("maxPrice") and float(p["maxPrice"]) > n else ""
    return ('<article class="sg" data-id="%s"><a class="pc-img" href="%s%s"><img src="%s" alt="%s" loading="lazy"></a><div class="pc-body"><span class="pc-tier">%s%s</span><h3 class="pc-name"><a href="%s%s" style="color:inherit;text-decoration:none">%s</a></h3>'
            '<div class="pc-price"><span class="pc-now">%s</span>%s%s</div><div class="pc-actions"><a class="btn btn-buy" href="%s" rel="noopener" data-buy="%s">Buy now</a><a class="btn btn-details" href="%s%s">Details</a></div></div></article>'
            % (p["id"], rel, p["path"], esc(p["image"]), esc(p["short"]), esc(p["typeName"]), esc(region_note(p)), rel, p["path"], esc(p["short"]), money(n), save, more, cart(p["variants"][0]["id"]), p["id"], rel, p["path"]))

def render(path_parts, title, desc, main, og_image=None, extra_ld=(), page_type="WebPage", route=None, sticky="", cta=None):
    rel = "../" * len(path_parts); path = "/".join(path_parts) + ("/" if path_parts else "")
    url = absurl(path) if SITE else None
    out = (tpl.replace("{{MAIN}}", main).replace("{{STICKY}}", sticky)
           .replace("{{ASSETS_HEAD}}", assets_head(rel))
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/site-index.js" defer></script>\n<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>\n<script src="%sshared/va.js" defer></script>' % (rel, rel, rel, rel))
           .replace("{{HEAD_EXTRA}}", head_extra(path, title, desc, og_image, rel, False, extra_ld, page_type))
           .replace("{{NAV_TOOLS}}", nav_tools(cta or '<a class="btn btn-buy" href="%s#contractor">Find my license</a>' % (rel or "./")))
           .replace("{{FOOTER}}", footer(rel)).replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(trim_desc(desc)))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % url) if url else "")
           .replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % esc(og_image)) if og_image else "")
           .replace("{{REL}}", rel).replace("{{HOME}}", rel or "./").replace("{{ROUTE}}", json.dumps(route or {"depth": len(path_parts)})))
    d = os.path.join(ROOT, *path_parts) if path_parts else ROOT
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    return url

FAMILY = {}
for _f, _ts in [("Online courses and practice", ["online-practice-exams", "online-course", "study-guide-online-course"]),
                ("Study guides, books and tabs", ["tabs", "study-guide", "study-guide-flash-cards", "code-book", "book-package", "highlighted-tabbed", "study-guide-nec-tabs", "study-guide-calculations-nec"]),
                ("Combos and complete packages", ["super-combo", "jump-start-package", "complete-package", "ultimate-combo", "nec-course-package", "ultimate-package", "exam-prep-package"]),
                ("Live training and rentals", ["live-training", "rental-package", "ultimate-rental"]),
                ("All-inclusive and licensing services", ["licensing-service", "the-1-package"])]:
    for _t in _ts: FAMILY[_t] = _f

THEMES = json.load(open(os.path.join(ROOT, "shared", "themes", "themes.json"), encoding="utf-8"))
DESIGN = str(CFG.get("design", 0) or 0)
def assets_head(rel):
    """Stylesheets, then the chosen design. Any page can preview another design with ?design=1..5 (0 = original);
    the choice is kept for the browser session so you can click around the site in it."""
    base = '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">\n<link rel="stylesheet" href="%sshared/va.css">' % (rel, rel, rel)
    t = THEMES.get(DESIGN)
    static = ('\n<link rel="stylesheet" id="dFont" href="%s">\n<link rel="stylesheet" id="dCss" href="%sshared/themes/%s.css">' % (t["fonts"], rel, DESIGN)) if t else ""
    loader = ('\n<script>(function(){var T=%s,d="%s",m=location.search.match(/[?&]design=(\\d)/);try{if(m)sessionStorage.setItem("vaDesign",m[1]);d=sessionStorage.getItem("vaDesign")||d;}catch(e){}'
              'if(d==="%s")return;var a=document.getElementById("dCss"),b=document.getElementById("dFont");if(a)a.remove();if(b)b.remove();var t=T[d];if(!t)return;'
              'document.write(\'<link rel="stylesheet" href="\'+t+\'"><link rel="stylesheet" href="%sshared/themes/\'+d+\'.css">\');})();</script>'
              % (json.dumps({k: v["fonts"] for k, v in THEMES.items()}), DESIGN, DESIGN, rel))
    return base + static + loader

# ---------- copy helpers ----------
def scope(c):
    if c["group"] == "officials": return vacopy.OFFICIAL_SCOPE.format(name=c["name"])
    return vacopy.SCOPE.get(c["slug"], "%s exam prep for the Virginia license." % c["name"])
def count_words(s): return len(re.sub(r"<[^>]+>", " ", s).split())
def plural(n, w): return "%d %s%s" % (n, w, "" if n == 1 else "s")
def cheapest(c): return min(c["products"], key=lambda p: float(p["price"]))
def priciest(c): return max(c["products"], key=lambda p: float(p["price"]))
def is_online(p): return p["type"] in ("online-course", "online-practice-exams", "licensing-service") or "Online" in p["title"]
def has_books(p): return p["type"] not in ("online-course", "online-practice-exams", "licensing-service")
def delivery(p):
    if p["type"] in ("online-course", "online-practice-exams"): return "Online access arrives by email after purchase"
    if p["type"] == "licensing-service": return "The service starts after purchase; we contact you for the details"
    if p["type"] in ("live-training", "rental-package", "ultimate-rental", "the-1-package", "study-guide-online-course", "complete-package", "ultimate-combo", "nec-course-package", "jump-start-package"):
        return "Books ship from our fulfillment center; online parts arrive by email"
    return "Books ship from our fulfillment center, %s" % FUL["name"]
def who_issues(c):
    return {"trades": "the Board for Contractors, through the DPOR Tradesmen program", "officials": "the Department of Housing and Community Development (DHCD)",
            "codes": "the board for the license you are sitting"}.get(c["group"], "the Board for Contractors at the Department of Professional and Occupational Regulation (DPOR)")
def open_book(c):
    if c["group"] == "officials": return "ICC certification exams are open book for most categories; the ICC bulletin for your exam lists the references allowed. Highlighted and tabbed books save the most time."
    return "Yes. The Virginia exams PSI runs are open book. You bring your own references, which may be highlighted and permanently tabbed; removable flags and loose notes are not allowed."
def class_faq(c):
    ps = c["products"]; n = c["name"]
    price_list = "; ".join("%s %s" % (p["typeName"] + region_note(p), money(p["price"])) for p in ps[:6]) + ("; and %d more" % (len(ps) - 6) if len(ps) > 6 else "")
    q = [("How much does %s exam prep cost?" % n, "%s exam prep runs from %s to %s across %s: %s." % (n, money(c["lo"]), money(c["hi"]), plural(len(ps), "option"), price_list)),
         ("Is the %s exam open book?" % n, open_book(c)),
         ("Who issues the %s license or certification in Virginia?" % n, "It comes from %s. Buying a package here does not register you or make you eligible; the board approves you first, and the exam vendor schedules the test." % who_issues(c))]
    if c["group"] in ("contractor", "business"):
        q.append(("Do I need the 8-hour pre-license course for a %s license?" % n, "Yes. Every Class A, B and C applicant completes 8 hours of pre-license education before the Board for Contractors issues the license. For Class A and B it is taken by the designated employee or a member of responsible management."))
        q.append(("What does the PSI exam cost?", "PSI charges $40 for one portion, $72 for two portions and $85 for three, paid to PSI. The fee is separate from the license application fee the board charges."))
    elif c["group"] == "trades":
        q.append(("What does the %s exam cost?" % n, "PSI charges $100 for a journeyman tradesman exam and $125 for a master exam, paid directly to PSI after the Board for Contractors approves you to sit it."))
        q.append(("How much continuing education does the license need?", "Renewing a journeyman or master license takes 3 hours of continuing education for electrical, plumbing and HVAC, and 1 hour for the gas fitting trades, from a board-approved provider."))
    elif c["group"] == "officials":
        q.append(("How long do I have to get certified after I am hired?", "Building, fire and property maintenance officials apply for DHCD certification within 12 months of hire; technical assistants such as inspectors and plans examiners have 18 months."))
        q.append(("What keeps the certification current?", "Certified code officials complete 16 hours of DHCD-approved continuing education every 2 years, plus any mandatory training such as code change classes."))
    elif c["group"] == "codes":
        q.append(("Which edition of a code book should I buy?", "The edition named in the candidate bulletin for your exam, which is not always the newest one. Virginia adopts new code editions on its own schedule, so check the bulletin before ordering."))
        q.append(("Can I bring a highlighted and tabbed code book into the exam?", "For the PSI exams run for the Board for Contractors, yes: highlighting, underlining and permanent tabs are allowed, while removable flags and loose notes are not."))
    q.append(("Are these the real exam questions?", "No. Licensing exam questions are confidential. The courses and practice exams are original material written to the same subjects and format, with explanations that point to the reference section."))
    q.append(("How do the books and courses arrive?", "Printed and rental books ship from our fulfillment center, %s. Online courses and practice exams arrive by email after purchase, so you can start the same day. Call %s with any question first." % (FUL["name"], CFG["phone"])))
    return q
def choose_text(c):
    ps = c["products"]; by = {p["type"]: p for p in ps}; n = c["name"]
    lo, hi = cheapest(c), priciest(c)
    parts = ["The %s at %s is the lightest way into the %s exam: %s." % (lo["typeName"], money(lo["price"]), n, vacopy.TYPE_BLURB.get(lo["type"], "exam prep"))]
    if "highlighted-tabbed" in by:
        h = by["highlighted-tabbed"]; parts.append("Highlighted and Tabbed Books at %s are the biggest time saver on an open-book test, because the references arrive ready for the exam room." % money(h["price"]))
    if "online-course" in by: parts.append("The Online Exam Prep Course at %s adds timed practice you can run on a phone between jobs." % money(by["online-course"]["price"]))
    if "live-training" in by: parts.append("Live Virtual Training at %s suits people who learn better with an instructor and a fixed schedule." % money(by["live-training"]["price"]))
    if hi["id"] != lo["id"]: parts.append("The %s at %s is the most complete option: %s." % (hi["typeName"], money(hi["price"]), vacopy.TYPE_BLURB.get(hi["type"], "everything in one order")))
    if len(parts) < 3: parts.append("Candidates who fail usually run out of time rather than knowledge, so pick the option that gets you fastest through the references, and call %s if you are unsure." % CFG["phone"])
    return " ".join(parts)

# ---------- remove previously generated folders ----------
manifest = os.path.join(ROOT, "generated-pages.txt")
KEEP = {"shared", "store", "content", "tools", "brand", "designs", ".git", ".github"}
if os.path.exists(manifest):
    for line in open(manifest):
        top = line.strip().split("/")[0]
        if top and top not in KEEP and os.path.isdir(os.path.join(ROOT, top)): shutil.rmtree(os.path.join(ROOT, top))
generated, urls = [], []

# ---------- home ----------
n_cls, n_prod = len(CLASSES), len(PRODUCTS)
lowest = min(float(p["price"]) for p in PRODUCTS)
def home_main():
    lead = ("Exam prep for %d Virginia licenses: contractor classes A, B and C, tradesman licenses for electricians, plumbers, HVAC and gas fitters, and ICC inspector and plans examiner certifications. "
            "Pick your license to compare its packages, from online courses to The 1 Package, then check out in one click." % n_cls)
    hero = ('<section class="hero" aria-labelledby="h1"><div class="wrap"><h1 id="h1">Virginia contractor exam prep for every license</h1><p class="lead" id="lead">%s</p>'
            '<form class="va-find" role="search" action="search/" method="get"><label for="findq" class="va-sr">Find your license</label><input id="findq" name="q" type="search" placeholder="Try roofing, master plumber or building inspector" autocomplete="off"><button class="btn btn-buy" type="submit">Find it</button></form>'
            '<div class="gauge"><div class="g hot"><b>%d</b><span>Virginia licenses covered</span></div><div class="g"><b>%d</b><span>packages, books and courses</span></div><div class="g"><b>%s</b><span>lowest starting price</span></div></div></div></section>'
            % (esc(lead), n_cls, n_prod, money(lowest)))
    tk = takeaways_html(["%d products across %d license classes, from %s to %s." % (n_prod, n_cls, money(lowest), money(max(float(p["price"]) for p in PRODUCTS))),
                         "Class A, B and C contractor applicants all complete 8 hours of pre-license education; Class A and B also pass PSI exams costing $40 to $85.",
                         "Tradesman exams cost $100 for journeyman and $125 for master, paid to PSI after board approval.",
                         "Every Buy now button goes straight to secure checkout at our fulfillment center, %s." % FUL["name"]])
    secs = []
    for g, gname, gblurb in vaclass.GROUPS:
        cl = classes_in(g)
        if not cl: continue
        items = "".join('<li><a href="%s/"><b>%s</b></a><span>%s from %s</span></li>' % (c["slug"], esc(c["name"]), plural(len(c["products"]), "option"), money(c["lo"])) for c in cl)
        secs.append('<section id="%s" class="va-group" aria-labelledby="h-%s"><div class="wrap"><h2 id="h-%s">%s</h2><p class="sub-h">%s</p><ul class="states-grid va-list">%s</ul></div></section>' % (g, g, g, esc(gname), esc(gblurb), items))
    classes_tbl = ('<section id="classes" class="center" aria-labelledby="h-classes"><div class="wrap"><h2 id="h-classes">How do Virginia contractor license classes work?</h2>'
                   '<p class="sub-h">The class decides how large a job your firm may take. The trade classification on the license decides what kind of work it may do, and each classification has its own exam.</p>'
                   '<div class="compare"><table><thead><tr><th>Class</th><th>Single contract</th><th>Total in 12 months</th><th>Exams</th></tr></thead><tbody>'
                   '<tr><td>Class C</td><td>$1,000 to under $10,000</td><td>Under $150,000</td><td>8-hour pre-license course; no PSI exam for most classifications</td></tr>'
                   '<tr><td>Class B</td><td>$10,000 to under $120,000</td><td>$150,000 to under $750,000</td><td>Virginia and general business portions plus the trade exam</td></tr>'
                   '<tr><td class="col-hot">Class A</td><td class="col-hot">$120,000 or more</td><td class="col-hot">$750,000 or more</td><td class="col-hot">Virginia, general and advanced business portions plus the trade exam</td></tr>'
                   '</tbody></table></div><p class="va-note">Limits from section 54.1-1100 of the Code of Virginia. Check the <a href="%s" rel="noopener" target="_blank">Board for Contractors</a> before applying, since limits and exam requirements change.</p></div></section>' % vacopy.DPOR_CONTRACTORS)
    types = {}
    for p in PRODUCTS: types.setdefault(p["type"], []).append(float(p["price"]))
    trows = "".join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%d</td></tr>' % (esc(dict((s, n) for s, n, _ in vaclass.TYPES).get(t, t)), esc(vacopy.TYPE_BLURB.get(t, "")), (money(min(v)) if min(v) == max(v) else "%s to %s" % (money(min(v)), money(max(v)))), len(v))
                    for t, v in sorted(types.items(), key=lambda kv: vaclass.TYPE_RANK.get(kv[0], 99)) if t in vaclass.TYPE_RANK and t not in ("exam-prep-package", "ultimate-package"))
    types_tbl = ('<section id="compare" style="background:#fff" aria-labelledby="h-compare"><div class="wrap center"><h2 id="h-compare">Which kind of package should you choose?</h2>'
                 '<p class="sub-h">Most licenses offer the same building blocks. Prices vary by license because the reference lists differ.</p>'
                 '<div class="compare"><table><thead><tr><th>Package</th><th>What you get</th><th>Price range</th><th>Products</th></tr></thead><tbody>%s</tbody></table></div></div></section>' % trows)
    how = ('<section id="how" class="center" aria-labelledby="h-how"><div class="wrap"><h2 id="h-how">How does buying work?</h2><div class="big">'
           '<div><b>1</b><h3>Find your license</h3><p>Every license page lists its packages, what each one includes and the price, plus how that exam works.</p></div>'
           '<div><b>2</b><h3>Pick a package</h3><p>Start with an online course, get the reference books highlighted and tabbed, or take The 1 Package with the paperwork done for you.</p></div>'
           '<div><b>3</b><h3>Check out in one click</h3><p>Buy now opens secure checkout at %s. Books ship from the fulfillment center and online courses arrive by email.</p></div></div></div></section>' % esc(FUL["name"]))
    pairs = HOME_FAQ
    faq = '<section id="faq" aria-labelledby="h-faq"><div class="wrap center"><h2 id="h-faq">What do people ask before buying?</h2>%s</div></section>' % faq_html(pairs)
    final = ('<section class="final" aria-labelledby="h-final"><div class="wrap"><h2 id="h-final">Your exam date is not moving. <em>Start today.</em></h2>'
             '<p>Find your license above, choose how much help you want, and check out in one click. Books ship from our fulfillment center, %s, and online courses arrive by email, so you can start the same day. Questions first? Call %s.</p>'
             '<a class="btn btn-buy" href="#contractor">Find my license</a></div></section>' % (esc(FUL["name"]), esc(CFG["phone"])))
    return hero + tk + "".join(secs) + classes_tbl + types_tbl + how + faq + sources_html("contractor", [("DHCD: earn a code official certification", vacopy.DHCD_CERT), ("DPOR Tradesmen program", vacopy.DPOR_TRADESMEN)]) + final, lead
HOME_FAQ = [
    ("Which Virginia license do I need?", "The right license depends on the work and the size of the jobs. Contractor firms need a Class A, B or C license with a classification for each trade they perform; individual electricians, plumbers, HVAC technicians and gas fitters need a tradesman license; and building inspectors and plans examiners need DHCD certification."),
    ("Are the Virginia contractor exams open book?", "Yes. The exams PSI runs for the Board for Contractors are open book. You bring your own references, which may be highlighted and permanently tabbed; removable flags and loose notes are not allowed."),
    ("Do I need the 8-hour pre-license course?", "Yes, for any Class A, B or C contractor license. The course is 8 hours and is taken by a member of responsible management or, for Class A and B, the designated employee."),
    ("What do the exams cost?", "Contractor exams cost $40 for one portion, $72 for two and $85 for three. Tradesman exams cost $100 for journeyman and $125 for master. Fees are paid to PSI, separately from the board's application fee."),
    ("Are these the real exam questions?", "No. Licensing exam questions are confidential. The courses and practice exams here are original material written to the same subjects and format, with explanations."),
    ("Does buying a package register me for the exam?", "No. The Board for Contractors, or DHCD for code officials, approves you first; PSI or ICC then schedules the exam. A package gets you ready for the test itself."),
    ("How do orders arrive?", "Books ship from our fulfillment center, %s; online courses and practice exams arrive by email after purchase. Rental books go back after your exam." % FUL["name"]),
    ("What is The 1 Package?", "The 1 Package is the all-inclusive option for a contractor classification: the exam prep, the reference books, help with the license application and the business setup, in one order."),
]
home_main_html, home_lead = home_main()
u = render([], "Virginia Contractor Exam Prep for Every License", "Virginia contractor exam prep for %d licenses: Class A, B and C trade classifications, tradesman licenses and ICC inspector exams. Books, courses and The 1 Package." % n_cls,
           home_main_html, CFG.get("logo"), [org_ld(), website_ld(), faq_ld(HOME_FAQ), crumbs_ld([("Home", "")])], route={"depth": 0, "home": True})
urls.append(u)

# ---------- license class pages + product pages ----------
def class_page(c):
    s, n, ps = c["slug"], c["name"], c["products"]
    lead = "%s Here are %s, from %s to %s, each with one-click checkout." % (scope(c), plural(len(ps), "package") if len(ps) > 1 else "the one package", money(c["lo"]), money(c["hi"]))
    if count_words(lead) < 40: lead += " Compare what each one includes, see how the exam works and find the answers to the questions people ask most."
    grp = c["group"]
    hero = ('<section class="hero hero--class" aria-labelledby="h1"><div class="wrap"><nav class="crumb" aria-label="Breadcrumb"><a href="../">All licenses</a><span>/</span><a href="../#%s">%s</a><span>/</span>%s</nav>'
            '<h1 id="h1">%s exam prep</h1><p class="lead" id="lead">%s</p><a class="btn btn-buy" href="#packs">See the %s</a></div></section>'
            % (grp, esc(GROUP_NAME[grp]), esc(n), esc(n), esc(lead), "packages" if len(ps) > 1 else "package"))
    tk = takeaways_html(["%s for the %s exam, from %s to %s." % (plural(len(ps), "option"), n, money(c["lo"]), money(c["hi"])),
                         vacopy.GROUP_FACTS[grp][0], vacopy.GROUP_FACTS[grp][2] if len(vacopy.GROUP_FACTS[grp]) > 2 else "",
                         "Buy now goes straight to secure checkout; books ship from %s and online courses arrive by email." % FUL["name"]])
    intro = '<p class="sub-h">Buy now adds the item to your cart and opens secure checkout at %s. Details shows the full description first.</p>' % esc(FUL["name"])
    if len(ps) <= 12:
        packs = ('<section id="packs" class="center" aria-labelledby="h-packs"><div class="wrap"><h2 id="h-packs">%s %s</h2>%s<div class="singles">%s</div></div></section>'
                 % (len(ps), esc(n + (" packages" if len(ps) > 1 else " package")), intro, "".join(card_html(p, "../") for p in ps)))
    else:
        fam = collections.OrderedDict()
        for p in ps: fam.setdefault(FAMILY.get(p["type"], "Other options"), []).append(p)
        blocks = []
        for i, (fname, fps) in enumerate(fam.items()):
            for j in range(0, len(fps), 12):
                chunk = fps[j:j + 12]; label = fname if len(fps) <= 12 else "%s, part %d" % (fname, j // 12 + 1)
                blocks.append('<section %sclass="center" aria-labelledby="h-fam-%d-%d"><div class="wrap"><h2 id="h-fam-%d-%d">%s %s: %s</h2>%s<div class="singles">%s</div></div></section>'
                              % ('id="packs" ' if not blocks else "", i, j, i, j, esc(n), "options" if len(chunk) > 1 else "option", esc(label.lower()),
                                 intro if not blocks else '<p class="sub-h">%s of the %d %s options, from %s.</p>' % (plural(len(chunk), "product"), len(ps), esc(n), money(min(float(q["price"]) for q in chunk))), "".join(card_html(p, "../") for p in chunk)))
        packs = "".join(blocks)
    compact = len(ps) > 14
    rows = "".join('<tr><td><a href="%s/">%s</a>%s</td>%s<td>%s</td></tr>' % (p["slug"], esc(p["typeName"]), esc((" " + p["year"]) if compact and p["year"] else "") + esc(region_note(p)), "" if compact else "<td>%s</td>" % esc(vacopy.TYPE_BLURB.get(p["type"], "exam prep")), money(p["price"])) for p in ps)
    compare = ('<section id="compare" style="background:#fff" aria-labelledby="h-compare"><div class="wrap center"><h2 id="h-compare">How do the %s options compare?</h2>'
               '<p class="sub-h">Prices are the starting price for each option; some offer add-ons at checkout.</p><div class="compare"><table><thead><tr><th>Option</th>%s<th>Price</th></tr></thead><tbody>%s</tbody></table></div></div></section>' % (esc(n), "" if compact else "<th>What you get</th>", rows))
    facts = "".join("<li>%s</li>" % esc(f) for f in vacopy.GROUP_FACTS[grp])
    how = ('<section id="exam" class="guide" aria-labelledby="h-exam"><div class="wrap"><h2 id="h-exam">How does the %s exam work?</h2><div class="guide-cols"><div><p>%s</p><ul class="va-facts">%s</ul></div>'
           '<div><h3 id="h-choose">Which %s option should I choose?</h3><p>%s</p></div></div></div></section>'
           % (esc(n), esc(vacopy.GROUP_HOW[grp].format(name=n)), facts, esc(n), esc(choose_text(c))))
    pairs = class_faq(c)
    faq = '<section id="faq" aria-labelledby="h-faq"><div class="wrap center"><h2 id="h-faq">%s exam questions</h2>%s</div></section>' % (esc(n), faq_html(pairs))
    sib = [x for x in classes_in(grp) if x["slug"] != s][:8]
    other_groups = [(g, gn) for g, gn, _ in vaclass.GROUPS if g != grp and classes_in(g)]
    related = ('<section class="related-pages" aria-labelledby="h-related-pages"><div class="wrap"><h2 id="h-related-pages">Related pages</h2><div class="rp-cols">'
               '<div><h3>More in %s</h3><ul>%s</ul></div><div><h3>Other license groups</h3><ul>%s</ul></div><div><h3>Also on this site</h3><ul><li><a href="../faq/">Virginia exam FAQ</a></li><li><a href="../blog/">Study tips and licensing news</a></li><li><a href="../#classes">Class A, B and C limits</a></li></ul></div></div></div></section>'
               % (esc(GROUP_NAME[grp].split(":")[0]), "".join('<li><a href="../%s/">%s</a></li>' % (x["slug"], esc(x["name"])) for x in sib) or '<li><a href="../">Every license</a></li>',
                  "".join('<li><a href="../#%s">%s</a></li>' % (g, esc(gn.split(":")[0])) for g, gn in other_groups)))
    main = hero + tk + packs + compare + how + faq + related + sources_html(grp)
    title = fit_title("Virginia %s Exam Prep" % n, "%s Exam Prep (Virginia)" % n, "%s Exam Prep" % n, "Virginia %s" % n)
    desc = "%s exam prep for Virginia: %s from %s to %s, including %s. One-click checkout." % (n, plural(len(ps), "option"), money(c["lo"]), money(c["hi"]), ", ".join(sorted({p["typeName"].lower() for p in ps})[:3]))
    lds = [{"@context": "https://schema.org", "@type": "CollectionPage", "name": "%s exam prep" % n, "url": absurl(s + "/"), "dateModified": TODAY, "publisher": publisher_ld(),
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(ps), "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absurl(p["path"]), "name": p["short"]} for i, p in enumerate(ps)]}},
           faq_ld(pairs), crumbs_ld([("All licenses", ""), (n, s + "/")])]
    sticky = '<div class="stickybar"><div><strong>%s</strong><small>%s from %s</small></div><a class="btn btn-buy" href="#packs">See options</a></div>' % (esc(n), plural(len(ps), "option"), money(c["lo"]))
    return render([s], title, desc, main, ps[-1]["image"], lds, page_type=None, route={"depth": 1, "cls": s}, sticky="", cta='<a class="btn btn-buy" href="#packs">See options</a>')

def first_sentence_fix(hx, subject):
    return re.sub(r"^(\s*(?:<p[^>]*>)?\s*)(This|These|It|They|That|Those|Such|Here)\b(\s+(?:\w+\s+){0,3}?(?:package|course|combo|bundle|set|guide|kit|book|books|product|option|training)\b)?",
                  lambda m: m.group(1) + "The " + subject, hx, count=1)

def product_page(c, p):
    parts = [c["slug"], p["slug"]]; rel = "../../"; path = "/".join(parts) + "/"
    full = FULL.get(p["id"], {"html": "", "images": [p["image"]]})
    hx = full.get("html") or ("<p>%s</p>" % esc(p.get("desc", "")))
    if FUL["name"] != BRAND: hx = re.sub(r"(?<![\w/.-])1 ?Exam ?Prep(?![\w.-])", BRAND, hx)
    if re.search(r"(\.\.\.|\u2026)\s*(</p>)?\s*$", hx):  # a truncated pull: end on the last full sentence
        hx = re.sub(r"(?s)^(.*[.!?])\s[^.!?]*(\.\.\.|\u2026)\s*(</p>)?\s*$", lambda m: m.group(1) + ("</p>" if m.group(3) else ""), hx)
    hx = first_sentence_fix(hx, p["short"])
    imgs = [u for u in (full.get("images") or []) if u] or [p["image"]]
    v0 = p["variants"][0]; c0, n0 = float(v0.get("compareAt") or 0), float(v0["price"])
    compare_html = ('<s class="pc-was" id="pWas">%s</s><span class="pc-save" id="pSave">Save %d%%</span>' % (money(c0), round((c0 - n0) / c0 * 100))) if c0 > n0 else '<s class="pc-was" id="pWas" hidden></s><span class="pc-save" id="pSave" hidden></span>'
    real_variants = len(p["variants"]) > 1 or p["variants"][0]["title"] not in ("Default Title", "")
    variants_html = "".join('<label class="m-opt"><input type="radio" name="v" value="%s"%s><span>%s</span><b>%s%s</b></label>' % (v["id"], " checked" if i == 0 else "", esc(v["title"]), money(v["price"]),
                            ('<s>%s</s>' % money(v["compareAt"])) if v.get("compareAt") and float(v["compareAt"]) > float(v["price"]) else "") for i, v in enumerate(p["variants"])) if real_variants else ""
    thumbs = "".join('<button type="button" data-src="%s" class="%s" aria-label="Image %d"><img src="%s" alt="%s, image %d" loading="lazy"></button>' % (esc(u), "on" if i == 0 else "", i + 1, esc(u), esc(p["short"]), i + 1) for i, u in enumerate(imgs)) if len(imgs) > 1 else ""
    blurb = vacopy.TYPE_BLURB.get(p["type"], "exam prep")
    where = "Virginia" if p["region"] == "Virginia" else ("%s, with the same ICC exam Virginia uses" % p["region"] if c["group"] == "officials" else p["region"])
    sub_parts = ["The %s is %s for the %s exam (%s), at %s%s." % (p["short"], blurb, c["name"], where, money(n0), (", %d%% off the %s list price" % (round((c0 - n0) / c0 * 100), money(c0))) if c0 > n0 else ""),
                 "%s." % delivery(p), "Buy now goes straight to secure checkout at %s." % FUL["name"], "Call %s with questions first." % CFG["phone"],
                 "It is one of %s for this license." % plural(len(c["products"]), "option") if len(c["products"]) > 1 else "No other option is listed for this license yet."]
    sub = sub_parts[0]
    for extra_s in sub_parts[1:]:
        if count_words(sub + " " + extra_s) <= 56: sub += " " + extra_s
    if count_words(sub) > 56:  # very long product names: name the type instead of repeating the full title
        sub = "This %s is %s for the %s exam (%s), at %s. %s." % (p["typeName"], blurb, c["name"], where, money(n0), delivery(p))
        sub = "The " + sub[5:]
    inc = ["%s: %s" % (p["typeName"], blurb), "Written for the %s exam%s" % (c["name"], region_note(p)), delivery(p)]
    if p.get("maxPrice") and float(p["maxPrice"]) > n0: inc.append("Options from %s to %s, chosen above before checkout" % (money(n0), money(p["maxPrice"])))
    included = '<ul class="included">%s</ul>' % "".join("<li>%s</li>" % esc(x) for x in inc)
    addons = [v["title"] for v in p["variants"][1:]]
    addons_html = ('<p class="addons"><b>Options at checkout:</b> %s. Pick one above and the price updates.</p>' % esc("; ".join([p["variants"][0]["title"]] + addons))) if addons else ""
    facts = "".join("<li>%s</li>" % esc(f) for f in vacopy.GROUP_FACTS[c["group"]])
    exam = '<h2 id="exam">How does the %s exam work?</h2><p>%s</p><ul class="va-facts">%s</ul>' % (esc(c["name"]), esc(vacopy.GROUP_HOW[c["group"]].format(name=c["name"])), facts)
    others = [q for q in c["products"] if q["id"] != p["id"]][:8]
    related = "".join('<a class="rel" href="../%s/"><img src="%s" alt="%s" loading="lazy"><span><b>%s</b><small>%s</small></span><span class="pc-now">%s</span></a>' % (
        q["slug"], esc(q["image"]), esc(q["short"]), esc(q["typeName"] + region_note(q)), esc(q["short"][:60] + ("…" if len(q["short"]) > 60 else "")), money(q["price"])) for q in others) or '<p>No other option is listed for this license yet.</p>'
    sib = [x for x in classes_in(c["group"]) if x["slug"] != c["slug"]][:5]
    more = '<div class="more-links"><h3>More %s</h3>%s<a href="%sfaq/">Virginia exam FAQ</a><a href="%sblog/">Study tips</a></div>' % (esc(GROUP_NAME[c["group"]].split(":")[0].lower()), "".join('<a href="%s%s/">%s</a>' % (rel, x["slug"], esc(x["name"])) for x in sib), rel, rel)
    pairs = [("How much is the %s?" % p["short"][:80], "%s%s. %s" % (money(n0), (" to %s depending on the option you pick" % money(p["maxPrice"])) if p.get("maxPrice") and float(p["maxPrice"]) > n0 else "", "The price at checkout is the one that applies, and it is shown before you pay.")),
             ("What is included?", "%s: %s. %s." % (p["typeName"], blurb, delivery(p))),
             ("Is the %s exam open book?" % c["name"], open_book(c)),
             ("Who issues the license or certification?", "It comes from %s. Buying study material does not register you or make you eligible to test." % who_issues(c)),
             ("Are these the real exam questions?", "No. Licensing exam questions are confidential. Courses and practice exams are original material written to the same subjects and format."),
             ("How fast can I start?", "Online courses and practice exams arrive by email after purchase. Books ship from our fulfillment center, %s; shipping options are shown at checkout." % FUL["name"])]
    if p["type"] in ("rental-package", "ultimate-rental"): pairs.append(("Do rental books have to go back?", "Yes. Rental books are returned after your exam, using the return instructions that come with the order. Buy the book package instead if you want to keep the references."))
    if p["type"] == "the-1-package": pairs.append(("What does The 1 Package cover beyond exam prep?", "It adds help with the Board for Contractors application and the business setup, so the paperwork moves while you study."))
    short_t = fit_title("Virginia %s %s" % (c["name"], p["typeName"]) + ("" if p["region"] == "Virginia" else " (%s)" % p["region"]),
                        "%s %s%s" % (c["name"], p["typeName"], region_note(p)), "%s: %s" % (c["name"].split(" (")[0], p["typeName"]), "%s %s" % (c["name"].split(" (")[0], p["typeName"]))
    if p["year"] and p["year"] not in short_t and len(short_t) + 7 <= 60: short_t += " (%s)" % p["year"]
    desc = trim_desc("%s for the Virginia %s exam: %s. %s. One-click checkout." % (p["typeName"], c["name"], blurb, money(n0)))
    if len(desc) < 70: desc = trim_desc(desc + " Fulfilled by %s; call %s with questions." % (FUL["name"], CFG["phone"]))
    jsonld = {"@context": "https://schema.org", "@type": "Product", "name": p["short"], "image": imgs[:6], "description": re.sub(r"\s+", " ", p.get("desc") or sub)[:500],
              "brand": {"@type": "Brand", "name": FUL["name"]}, "sku": p["id"], "productID": p["id"], "category": "%s exam prep" % c["name"], "url": absurl(path),
              "offers": [{"@type": "Offer", "name": v["title"], "priceCurrency": "USD", "price": v["price"], "availability": "https://schema.org/InStock" if v.get("available", True) else "https://schema.org/OutOfStock",
                          "itemCondition": "https://schema.org/NewCondition", "url": absurl(path), "seller": {"@type": "Organization", "name": BRAND}} for v in p["variants"]]}
    crumbs = [("All licenses", ""), (c["name"], c["slug"] + "/"), (p["typeName"], path)]
    extra = head_extra(path, short_t, desc, imgs[0], rel, False, [crumbs_ld(crumbs), faq_ld(pairs)], page_type="WebPage", about="%s exam" % c["name"])
    pjson = json.dumps({"id": p["id"], "variants": p["variants"], "title": p["short"], "state": c["name"], "level": GROUP_NAME[c["group"]], "tierName": p["typeName"], "price": p["price"]})
    kicker = "%s · %s%s" % (c["name"], p["typeName"], region_note(p))
    out = (ptpl.replace("{{TITLE}}", esc(short_t)).replace("{{DESC}}", esc(desc))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % absurl(path)) if SITE else "")
           .replace("{{OGIMAGE}}", '<meta property="og:image" content="%s">\n' % esc(imgs[0]))
           .replace("{{ASSETS_HEAD}}", assets_head(rel))
           .replace("{{ASSETS_PRODUCT}}", '<script src="%sshared/product.js"></script>' % rel)
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/site-index.js" defer></script>\n<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel, rel)).replace("{{HEAD_EXTRA}}", extra)
           .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="%s" rel="noopener">Buy now</a>' % cart(v0["id"])))
           .replace("{{FOOTER}}", footer(rel)).replace("{{ROUTE}}", json.dumps({"depth": 2, "cls": c["slug"], "product": p["slug"]}))
           .replace("{{JSONLD}}", json.dumps(jsonld, ensure_ascii=False)).replace("{{P_JSON}}", pjson)
           .replace("{{HOME}}", rel).replace("{{CLASS}}", esc(c["name"])).replace("{{GROUP}}", c["group"]).replace("{{GROUP_NAME}}", esc(GROUP_NAME[c["group"]].split(":")[0]))
           .replace("{{TYPE_NAME}}", esc(p["typeName"])).replace("{{KICKER}}", esc(kicker)).replace("{{H1}}", esc(p["short"])).replace("{{SUB}}", esc(sub))
           .replace("{{IMAGE}}", esc(imgs[0])).replace("{{IMAGE_ALT}}", esc(p["short"])).replace("{{THUMBS}}", thumbs)
           .replace("{{PRICE}}", money(n0)).replace("{{COMPARE_HTML}}", compare_html).replace("{{VARIANTS_HTML}}", variants_html).replace("{{DELIVERY}}", esc(delivery(p)))
           .replace("{{BUY_URL}}", cart(v0["id"])).replace("{{MORE_LINKS_HTML}}", more)
           .replace("{{TAKEAWAYS_HTML}}", takeaways_html(["%s: %s%s." % (p["typeName"], money(n0), (", down from %s" % money(c0)) if c0 > n0 else ""), "For the %s exam%s; %s." % (c["name"], region_note(p), blurb),
                                                          vacopy.GROUP_FACTS[c["group"]][0], "%s. Buying does not grant exam eligibility." % delivery(p)]))
           .replace("{{INCLUDED_HTML}}", included).replace("{{ADDONS_HTML}}", addons_html).replace("{{DESCRIPTION_HTML}}", hx).replace("{{EXAM_HTML}}", exam)
           .replace("{{RELATED_HTML}}", related).replace("{{FAQ_HTML}}", "".join('<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if i == 0 else "", esc(q), esc(a)) for i, (q, a) in enumerate(pairs)))
           .replace("{{SOURCES_HTML}}", sources_html(c["group"]).replace('<section class="wrap sources"', '<section class="sources"')))
    d = os.path.join(ROOT, *parts); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    return absurl(path)

for s in ORDER:
    if s not in CLASSES: continue
    c = CLASSES[s]
    urls.append(class_page(c)); generated.append(s)
    for p in c["products"]:
        urls.append(product_page(c, p)); generated.append(p["path"].rstrip("/"))
with open(manifest, "w") as f: f.write("\n".join(generated) + "\n")

# ---------- site index for search (independent of the catalog format) ----------
idx = {"classes": [{"n": c["name"], "u": c["slug"] + "/", "g": GROUP_NAME[c["group"]], "k": len(c["products"]), "lo": c["lo"]} for c in (CLASSES[s] for s in ORDER if s in CLASSES)],
       "products": [{"t": p["short"], "c": p["clsName"], "y": p["typeName"] + region_note(p), "p": float(p["price"]), "i": p["image"], "u": p["path"]} for p in PRODUCTS]}
open(os.path.join(ROOT, "shared", "site-index.js"), "w", encoding="utf-8").write("/* Generated by build.py for site search. */\nwindow.SITE_INDEX=%s;\n" % json.dumps(idx, separators=(",", ":"), ensure_ascii=False))

# ---------- 404: unknown paths go to the closest real page ----------
nf = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Page not found</title><meta name="robots" content="noindex">
<script>(function(){var S=%s;var p=location.pathname.split("/").filter(Boolean).map(function(x){return x.toLowerCase();});
for(var k=0;k<p.length;k++){if(S.indexOf(p[k])>-1){location.replace("/"+p.slice(0,k+1).join("/")+"/");return;}}location.replace("/");})();</script>
</head><body><h1>Taking you to the right page</h1><p><a href="/">Every Virginia license</a></p></body></html>""" % json.dumps(sorted(CLASSES))
open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(nf)

# ---------- /search/ ----------
sp_main = ('<section class="wrap search-page"><h1 id="h1">Search</h1><form id="searchPage" class="srch-form" role="search"><input class="srch-q" name="q" type="search" placeholder="License, package or product" aria-label="Search" autocomplete="off"><button class="btn btn-buy" type="submit">Search</button></form><div id="searchOut"></div></section>')
render(["search"], "Search | " + BRAND, "Search %s exam prep by license, package type or product name." % BRAND, sp_main, CFG.get("logo"), route={"depth": 1, "search": True})
p_ = os.path.join(ROOT, "search", "index.html"); s_ = open(p_, encoding="utf-8").read().replace('content="index, follow, max-image-preview:large"', 'content="noindex, nofollow"')
s_ = re.sub(r'<link rel="alternate" type="text/markdown"[^>]*>\n', "", s_); s_ = re.sub(r'<script type="application/ld\+json">\{"@context": "https://schema.org", "@type": "WebPage".*?</script>\n', "", s_, flags=re.S)
open(p_, "w", encoding="utf-8").write(s_)

# ---------- /admin/ ----------
atpl = open(os.path.join(ROOT, "store", "admin.html"), encoding="utf-8").read()
admin_cfg = {"gtagId": CFG.get("gtagId", ""), "ga4PropertyId": CFG.get("ga4PropertyId", ""), "googleOAuthClientId": CFG.get("googleOAuthClientId", ""), "repo": CFG.get("repo", ""), "siteUrl": SITE or ""}
os.makedirs(os.path.join(ROOT, "admin"), exist_ok=True)
open(os.path.join(ROOT, "admin", "index.html"), "w", encoding="utf-8").write(brand_tokens(atpl.replace("{{ADMIN_JSON}}", json.dumps(admin_cfg))))

# ---------- blog ----------
ALL_POSTS = blogkit.load_posts(os.path.join(ROOT, "content", "posts"), SITE or "")
POSTS = [q for q in ALL_POSTS if q.get("kind", "blog") != "page"]
PAGES = [q for q in ALL_POSTS if q.get("kind", "blog") == "page"]
btpl = open(os.path.join(ROOT, "store", "blog-post.html"), encoding="utf-8").read()
bitpl = open(os.path.join(ROOT, "store", "blog-index.html"), encoding="utf-8").read()
BLOG_FAQ = [("How long should I study for a Virginia contractor exam?", "Most candidates do well with six to eight weeks at about 90 minutes a day, split between finding answers fast in the references, the business and law material, and full-length timed practice in the last two weeks."),
            ("Is the exam open book, and which books do I bring?", "The PSI contractor and tradesman exams are open book. Bring the editions named in your candidate bulletin; highlighting and permanent tabs are allowed, removable flags and loose notes are not."),
            ("What is the difference between Class A, B and C?", "The class sets the size of job your firm may take: Class C up to under $10,000 a job, Class B up to under $120,000 a job and $750,000 a year, Class A above that. Class A and B also need the business exams."),
            ("Are the practice questions the real exam questions?", "No. Licensing exam questions are confidential and are not published. Practice questions are original material written to the same subjects and format."),
            ("Does buying a package register me for the exam?", "No. The Board for Contractors approves you first, and PSI schedules the exam. Code officials go through DHCD and ICC instead."),
            ("How do the packages arrive?", "Books ship from our fulfillment center, %s; online courses arrive by email after purchase, so you can start the same day." % FUL["name"])]
def nice_date(d): return nice_day(d)
def post_card(q, rel):
    img = ('<img src="%s" alt="%s" loading="lazy">' % (esc(q["image"]), esc(q["title"]))) if q["image"] else ('<div class="noimg">%s</div>' % esc(q["title"][:48]))
    return ('<a class="card" href="%sblog/%s/" data-track="blog_card">%s<div class="card-body"><p class="post-meta"><time datetime="%s">%s</time><span>%d min read</span></p><h2>%s</h2><p>%s</p></div></a>'
            % (rel, q["slug"], img, q["date"], nice_date(q["date"]), max(1, round(q["words"] / 220)), esc(q["title"]), esc(q["excerpt"])))
def blog_common(out, rel, path, title, desc, image, lds, route, noindex=False, page_type="WebPage"):
    desc = trim_desc(desc)
    return (out.replace("{{TITLE}}", esc(title)).replace("{{DESC}}", esc(desc)).replace("{{BRAND}}", esc(BRAND))
            .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % absurl(path)) if SITE else "")
            .replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % esc(image)) if image else "")
            .replace("{{HEAD_EXTRA}}", head_extra(path, title, desc, image, rel, noindex, lds, page_type))
            .replace("{{ASSETS_HEAD}}", assets_head(rel))
            .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/site-index.js" defer></script>\n<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel, rel))
            .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="%s#contractor">Find my license</a>' % rel)).replace("{{FOOTER}}", footer(rel))
            .replace("{{ROUTE}}", json.dumps(route)).replace("{{REL}}", rel).replace("{{HOME}}", rel))
blog_dir = os.path.join(ROOT, "blog"); shutil.rmtree(blog_dir, ignore_errors=True); os.makedirs(blog_dir, exist_ok=True)
all_tags = sorted({t for q in POSTS for t in q["tags"]}, key=str.lower)
def blog_index(dest_parts, posts, tag=None):
    rel = "../" * len(dest_parts); path = "/".join(dest_parts) + "/"
    title = ("Posts tagged %s | %s" % (tag, BRAND)) if tag else "Virginia Contractor Exam Blog: Study Tips and Rules"
    desc = ("Posts tagged %s from the %s blog." % (tag, BRAND)) if tag else "Study plans, Virginia licensing rules and exam strategy for contractor, tradesman and code official exams, from %s." % BRAND
    h1 = ("Posts tagged “%s”" % tag) if tag else "The Virginia contractor exam blog"
    lead = ("%d post%s." % (len(posts), "" if len(posts) == 1 else "s")) if tag else ("Study plans, Virginia licensing rules and exam strategy for the contractor, tradesman and code official exams. Each post links to the license it covers, and every rule we quote links back to the board that sets it, so you can check it yourself before you apply.")
    feat, rest = (posts[0], posts[1:]) if posts and not tag else (None, posts)
    feat_html = ""
    if feat:
        fimg = ('<img src="%s" alt="%s">' % (esc(feat["image"]), esc(feat["title"]))) if feat["image"] else ""
        feat_html = ('<a class="feature%s" href="%sblog/%s/" data-track="blog_featured">%s<div><span class="pc-tier">Latest</span><h2>%s</h2><p>%s</p><p class="post-meta"><time datetime="%s">%s</time><span>%d min read</span></p></div></a>'
                     % ("" if fimg else " noimg", rel, feat["slug"], fimg, esc(feat["title"]), esc(feat["excerpt"]), feat["date"], nice_date(feat["date"]), max(1, round(feat["words"] / 220))))
    tagf = ('<nav class="tagbar" aria-label="Topics"><a class="tag" href="%sblog/"%s>All</a>%s</nav>' % (rel, "" if tag else ' aria-current="page"', "".join('<a class="tag" href="%sblog/tag/%s/"%s>%s</a>' % (rel, blogkit.slugify(t), ' aria-current="page"' if tag == t else "", esc(t)) for t in all_tags))) if all_tags else ""
    cards = "".join(post_card(q, rel) for q in rest)
    empty = '' if posts else '<p class="empty">No posts yet. The first one is on its way.</p>'
    lds = [crumbs_ld([("Home", ""), ("Blog", "blog/")] + ([(tag, path)] if tag else [])),
           {"@context": "https://schema.org", "@type": "Blog" if not tag else "CollectionPage", "name": h1, "url": absurl(path), "publisher": publisher_ld(), "dateModified": TODAY,
            "blogPost" if not tag else "hasPart": [{"@type": "BlogPosting", "headline": q["title"], "url": absurl("blog/%s/" % q["slug"]), "datePublished": q["date"]} for q in posts[:20]]}]
    if not tag: lds.append(faq_ld(BLOG_FAQ))
    out = blog_common(bitpl, rel, path, title, desc, (feat or {}).get("image") or CFG.get("logo"), lds, {"depth": len(dest_parts), "blog": True}, noindex=bool(tag), page_type=None)
    out = out.replace("{{YEAR}}", TODAY[:4])
    intro = "" if tag else ('<div class="blog-intro"><p>Most people who fail a licensing exam do not fail on knowledge. They run out of time in the references, misread an exception, or bring the wrong edition. New posts land here first and in the <a href="%sblog/feed.xml">RSS feed</a>. When a post is about one license, it links straight to that license page so you can act on it.</p></div>' % rel)
    btk = takeaways_html(["%d post%s so far%s, written for Virginia contractor, tradesman and code official candidates." % (len(posts), "" if len(posts) == 1 else "s", (" tagged %s" % tag) if tag else ""),
                          "Topics: %s." % ", ".join(all_tags[:8]) if all_tags else "Topics cover study strategy, using the references and Virginia licensing rules.",
                          "Exam prep for %d Virginia licenses, with every rule linked to the board that sets it." % n_cls,
                          "New posts appear in the RSS feed at /blog/feed.xml the moment they are published."])
    out = out.replace("{{BLOG_FAQ_HTML}}", "".join('<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if i == 0 else "", esc(q), esc(a)) for i, (q, a) in enumerate(BLOG_FAQ)))
    out = out.replace("{{TAKEAWAYS_HTML}}", btk).replace("{{INTRO_HTML}}", intro).replace("{{H1}}", esc(h1)).replace("{{LEAD}}", esc(lead)).replace("{{TAG_FILTER}}", tagf).replace("{{FEATURED_HTML}}", feat_html).replace("{{CARDS_HTML}}", cards).replace("{{EMPTY_HTML}}", empty)
    if not tag: out = out.replace("</main>", sources_html("contractor", [("DPOR Tradesmen program", vacopy.DPOR_TRADESMEN), ("DHCD: earn a code official certification", vacopy.DHCD_CERT)]).replace('<section class="wrap sources"', '<section class="sources"') + "\n</main>", 1)
    d = os.path.join(ROOT, *dest_parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    if SITE and not tag: urls.append(absurl(path))
blog_index(["blog"], POSTS)
for t in all_tags: blog_index(["blog", "tag", blogkit.slugify(t)], [q for q in POSTS if t in q["tags"]], t)
from urllib.parse import quote
pages_dir = os.path.join(ROOT, "pages"); shutil.rmtree(pages_dir, ignore_errors=True)
def license_for(q):
    v = (q.get("state") or "").strip().lower()
    return next((c for c in CLASSES.values() if v and (v == c["slug"] or v == c["name"].lower())), None)
for q in POSTS + PAGES:
    is_page = q.get("kind") == "page"
    parts = ["pages" if is_page else "blog", q["slug"]]; rel = "../../"; path = "%s/%s/" % (parts[0], q["slug"]); url = absurl(path)
    lic = license_for(q)
    if lic:
        cta_url = "%s%s/" % (rel, lic["slug"]); cta_kicker = lic["name"]; cta_title = "Ready to study for the %s exam?" % lic["name"]
        cta_text = "%s from %s, with one-click checkout." % (plural(len(lic["products"]), "option"), money(lic["lo"])); cta_label = "See %s options" % lic["name"].split(" (")[0]
        more_link = '<a href="%s">%s</a>' % (cta_url, esc(lic["name"]))
    else:
        cta_url = rel + "#contractor"; cta_kicker = "Ready to study?"; cta_title = "Find your license, then choose a package."; cta_text = "Exam prep for %d Virginia contractor, tradesman and inspector licenses." % n_cls; cta_label = "Find my license"; more_link = ""
    related = [r for r in POSTS if r["slug"] != q["slug"] and (set(r["tags"]) & set(q["tags"]))][:3] or [r for r in POSTS if r["slug"] != q["slug"]][:3]
    rel_html = ('<section class="related-posts" aria-labelledby="h-more"><h2 id="h-more">Keep reading</h2><div class="post-grid">%s</div></section>' % "".join(post_card(r, rel) for r in related)) if related else ""
    tags_html = ('<nav class="tagbar" aria-label="Topics">%s</nav>' % "".join('<a class="tag" href="%sblog/tag/%s/">%s</a>' % (rel, blogkit.slugify(t), esc(t)) for t in q["tags"])) if q["tags"] else ""
    hero = ('<figure class="hero"><img src="%s" alt="%s" fetchpriority="high"></figure>' % (esc(q["image"]), esc(q["title"]))) if q["image"] and ('src="%s"' % q["image"]) not in q["html"] else ""
    lds = [crumbs_ld([("Home", ""), ("Blog", "blog/"), (q["title"], path)]),
           {"@context": "https://schema.org", "@type": "BlogPosting", "headline": q["title"][:110], "description": q["excerpt"], "image": [q["image"]] if q["image"] else None, "datePublished": q["date"], "dateModified": q["updated"],
            "author": {"@type": "Organization" if not q["author"] or q["author"] == BRAND else "Person", "name": q["author"] or BRAND}, "publisher": publisher_ld(),
            "mainEntityOfPage": url, "url": url, "wordCount": q["words"], "keywords": ", ".join(q["tags"]) or None, "articleSection": "Virginia Contractor Exam Prep", "inLanguage": "en-US"}]
    lds[1] = {k: v for k, v in lds[1].items() if v}
    ptitle = q.get("meta_title") or (q["title"] if len(q["title"]) + len(BRAND) + 3 > 60 else "%s | %s" % (q["title"], BRAND))
    pdesc = q.get("meta_description") or q["excerpt"]
    if is_page: lds[0] = crumbs_ld([("Home", ""), (q["title"], path)]); lds[1]["@type"] = "Article"
    out = blog_common(btpl, rel, path, ptitle, pdesc, q["image"] or CFG.get("logo"), lds, {"depth": 2, "blog": True, "post": q["slug"]}, page_type=None)
    if is_page: out = out.replace('<a href="{{REL}}blog/">Blog</a><span>/</span>', "").replace('<p class="post-meta">', '<p class="post-meta" hidden>')
    out = (out.replace("{{H1}}", esc(q["title"])).replace("{{TITLE_SHORT}}", esc(q["title"][:60] + ("…" if len(q["title"]) > 60 else ""))).replace("{{EXCERPT}}", esc(q["excerpt"]))
           .replace("{{DATE}}", q["date"]).replace("{{UPDATED}}", q["updated"]).replace("{{DATE_NICE}}", nice_date(q["date"])).replace("{{AUTHOR_HTML}}", ('<span>%s</span>' % esc(q["author"])) if q["author"] else "")
           .replace("{{READ_MIN}}", str(max(1, round(q["words"] / 220)))).replace("{{TAGS_HTML}}", tags_html).replace("{{HERO_HTML}}", hero).replace("{{TAKEAWAYS_HTML}}", takeaways_html(q.get("takeaways") or [])).replace("{{BODY_HTML}}", q["html"])
           .replace("{{URL_ENC}}", quote(url, safe="")).replace("{{TITLE_ENC}}", quote(q["title"], safe="")).replace("{{MORE_LINK}}", more_link)
           .replace("{{CTA_KICKER}}", esc(cta_kicker)).replace("{{CTA_TITLE}}", esc(cta_title)).replace("{{CTA_TEXT}}", esc(cta_text)).replace("{{CTA_URL}}", cta_url).replace("{{CTA_LABEL}}", esc(cta_label))
           .replace("{{RELATED_HTML}}", rel_html))
    d = os.path.join(ROOT, *parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    if SITE: urls.append(url)
rpath = os.path.join(ROOT, "content", "redirects.json")
if os.path.exists(rpath):
    try: RED = json.load(open(rpath, encoding="utf-8"))
    except Exception: RED = {}
    for old, new in RED.items():
        old = old.strip("/"); new = new.strip("/")
        if not old or old == new or os.path.exists(os.path.join(ROOT, *old.split("/"), "index.html")): continue
        target = absurl(new + "/")
        os.makedirs(os.path.join(ROOT, *old.split("/")), exist_ok=True)
        open(os.path.join(ROOT, *old.split("/"), "index.html"), "w", encoding="utf-8").write('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex"><link rel="canonical" href="%s"><meta http-equiv="refresh" content="0; url=%s"><script>location.replace(%s)</script></head><body><p>This page has moved to <a href="%s">%s</a>.</p></body></html>' % (esc(target), esc(target), json.dumps(target), esc(target), esc(target)))
feed_items = "".join("<item><title>%s</title><link>%s</link><guid isPermaLink=\"true\">%s</guid><pubDate>%s</pubDate><description>%s</description></item>\n" % (
    esc(q["title"]), absurl("blog/%s/" % q["slug"]), absurl("blog/%s/" % q["slug"]), datetime.datetime.fromisoformat(q["date"][:10]).strftime("%a, %d %b %Y 09:00:00 -0500"), esc(q["excerpt"])) for q in POSTS[:30])
open(os.path.join(blog_dir, "feed.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s Blog</title><link>%s</link><description>Virginia contractor exam study tips and licensing news.</description><language>en-us</language>\n%s</channel></rss>\n' % (esc(BRAND), absurl("blog/"), feed_items))
open(os.path.join(blog_dir, "posts.json"), "w", encoding="utf-8").write(json.dumps([{k: q[k] for k in ("slug", "title", "date", "updated", "excerpt", "image", "tags", "state", "level", "author", "words")} for q in POSTS], ensure_ascii=False))

# ---------- /faq/ ----------
ftpl = open(os.path.join(ROOT, "store", "faq.html"), encoding="utf-8").read()
GEN_FAQ = json.load(open(os.path.join(ROOT, "content", "faq-general.json"), encoding="utf-8"))["categories"]
shutil.rmtree(os.path.join(ROOT, "faq"), ignore_errors=True)
gen_pairs = [(q, a.replace("1 Exam Prep", FUL["name"])) for cg in GEN_FAQ for q, a in cg["items"]]
sections = [(cg["slug"], cg["name"], len(cg["items"]), faq_html([(q, a.replace("1 Exam Prep", FUL["name"])) for q, a in cg["items"]])) for cg in GEN_FAQ]
lic_list = "".join('<li><a href="../%s/#faq">%s</a></li>' % (c["slug"], esc(c["name"])) for c in (CLASSES[s] for s in ORDER if s in CLASSES))
sections.append(("licenses", "Where are the questions for my license?", n_cls, '<p class="faq-count">Every license page ends with its own questions: the price range, open-book rules, who issues the license and the exam fee. Pick yours below.</p><ul class="faq-states">%s</ul>' % lic_list))
jump = "".join('<a class="tag" href="#%s">%s <small>%d</small></a>' % (sid, esc(name), n) for sid, name, n, _ in sections)
secs = "".join('<section class="faq-sec" aria-labelledby="%s"><h2 id="%s">%s</h2>%s</section>' % (sid, sid, esc(name), body) for sid, name, n, body in sections)
flead = ("%d answers about Virginia contractor, tradesman and code official exams: the Class A, B and C limits, the 8-hour pre-license course, PSI exam fees, open-book rules, studying and ordering. Each of the %d license pages adds 7 questions of its own, linked at the bottom of this page." % (len(gen_pairs), n_cls))
ftitle = fit_title("Virginia Contractor Exam FAQ: %d Answers" % len(gen_pairs))
fdesc = trim_desc(flead)
lds = [crumbs_ld([("Home", ""), ("FAQ", "faq/")]), faq_ld(gen_pairs[:80])]
fout = (ftpl.replace("{{TITLE}}", esc(ftitle)).replace("{{DESC}}", esc(fdesc)).replace("{{BRAND}}", esc(BRAND))
        .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % absurl("faq/")) if SITE else "").replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % esc(CFG.get("logo"))) if CFG.get("logo") else "")
        .replace("{{HEAD_EXTRA}}", head_extra("faq/", ftitle, fdesc, CFG.get("logo"), "../", False, lds))
        .replace("{{ASSETS_HEAD}}", assets_head("../"))
        .replace("{{ASSETS_SEARCH}}", '<script src="../shared/site-index.js" defer></script>\n<script src="../shared/search.js" defer></script>\n<script src="../shared/track.js" defer></script>')
        .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="../#contractor">Find my license</a>')).replace("{{FOOTER}}", footer("../"))
        .replace("{{ROUTE}}", json.dumps({"depth": 1, "faq": True})).replace("{{REL}}", "../").replace("{{HOME}}", "../")
        .replace("{{CRUMB_HTML}}", '<a href="../">Home</a><span>/</span>FAQ').replace("{{H1}}", "Virginia contractor exam FAQ").replace("{{LEAD}}", esc(flead))
        .replace("{{TAKEAWAYS_HTML}}", takeaways_html(["%d questions answered here, plus 7 more on each of the %d license pages." % (len(gen_pairs), n_cls),
                                                         "Class C covers jobs of $1,000 to under $10,000; Class B up to under $120,000 a job and $750,000 a year; Class A has no upper limit.",
                                                         "PSI contractor exams cost $40 to $85; tradesman exams cost $100 for journeyman and $125 for master.",
                                                         "Every exam PSI runs for the board is open book, with highlighting and permanent tabs allowed."]))
        .replace("{{JUMP_HTML}}", jump).replace("{{SECTIONS_HTML}}", secs)
        .replace("{{CTA_KICKER}}", "Ready to study?").replace("{{CTA_TITLE}}", "Find your license, then choose a package.").replace("{{CTA_TEXT}}", esc("Exam prep for %d Virginia licenses, from %s. Buy buttons go straight to checkout." % (n_cls, money(lowest))))
        .replace("{{CTA_URL}}", "../#contractor").replace("{{CTA_LABEL}}", "Find my license")
        .replace("{{RELATED_HTML}}", sources_html("contractor", [("DPOR Tradesmen program", vacopy.DPOR_TRADESMEN), ("DHCD: earn a code official certification", vacopy.DHCD_CERT)]).replace('<section class="wrap sources"', '<section class="sources"')).replace("{{MORE_LINK}}", ""))
os.makedirs(os.path.join(ROOT, "faq"), exist_ok=True); open(os.path.join(ROOT, "faq", "index.html"), "w", encoding="utf-8").write(anchor_ids(fout))
urls.append(absurl("faq/"))

# ---------- icons + manifest (text logo until brand/logo-source.png is added and tools/make_logo.py is run) ----------
fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1b1f3b"/><path d="M12 33 32 15l20 18h-6v16H18V33z" fill="#ff5a1f"/><rect x="28" y="37" width="8" height="12" fill="#1b1f3b"/></svg>'
if not HAS_PNG_ICONS:
    open(os.path.join(ROOT, "shared", "favicon.svg"), "w").write(fav)
    try:
        from PIL import Image, ImageDraw, ImageFont
        def font(sz):
            for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
                if os.path.exists(f): return ImageFont.truetype(f, sz)
            return ImageFont.load_default()
        house = lambda sc, ox, oy: [(ox + x * sc, oy + y * sc) for x, y in [(12, 33), (32, 15), (52, 33), (46, 33), (46, 49), (18, 49), (18, 33)]]
        im = Image.new("RGBA", (180, 180), (27, 31, 59, 255)); dr = ImageDraw.Draw(im); dr.polygon(house(2.6, 7, 7), fill=(255, 90, 31, 255)); im.save(os.path.join(ROOT, "shared", "apple-touch-icon.png"))
        lg = Image.new("RGB", (1200, 630), (27, 31, 59)); d = ImageDraw.Draw(lg); d.polygon(house(4.2, 70, 140), fill=(255, 90, 31))
        lines, cur = [], ""
        for w in BRAND.split():
            t = (cur + " " + w).strip()
            if d.textlength(t, font=font(74)) > 800: lines.append(cur); cur = w
            else: cur = t
        lines.append(cur); y = 300 - 44 * len(lines)
        for ln in lines: d.text((340, y), ln, font=font(74), fill="white"); y += 88
        tl, tcur, tlines = CFG.get("tagline", "").split(), "", []
        for w in tl:
            t = (tcur + " " + w).strip()
            if d.textlength(t, font=font(30)) > 800: tlines.append(tcur); tcur = w
            else: tcur = t
        tlines.append(tcur)
        for ln in tlines[:2]: d.text((340, y + 10), ln, font=font(30), fill=(255, 176, 143)); y += 40
        d.text((340, 560), "Fulfilled by %s" % FUL["name"], font=font(24), fill=(170, 175, 205))
        lg.save(os.path.join(ROOT, "shared", "logo.png"), optimize=True)
    except Exception as e: print("logo images skipped:", e)
open(os.path.join(ROOT, "manifest.webmanifest"), "w").write(json.dumps({"name": BRAND, "short_name": "VA Contractor", "start_url": "./", "display": "browser", "background_color": "#f7f6f2", "theme_color": "#1b1f3b",
    "icons": ([{"src": "shared/logo-mark.png", "sizes": "512x512", "type": "image/png"}] if HAS_PNG_ICONS else []) + [{"src": "shared/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}] + ([] if HAS_PNG_ICONS else [{"src": "shared/favicon.svg", "sizes": "any", "type": "image/svg+xml"}])}, indent=1))


# ---------- /designs/: compare the five designs (noindex) ----------
dd = os.path.join(ROOT, "designs"); os.makedirs(dd, exist_ok=True)
cards = []
for k in ["0"] + sorted(THEMES):
    t = THEMES.get(k, {"name": "Original", "about": "The template look: navy, orange and Archivo Black."})
    shots = "".join('<a href="../%s?design=%s"><img src="%s-%s.png" alt="%s design, %s page" loading="lazy"></a>' % (u, k, k, pg, esc(t["name"]), lab) for pg, u, lab in (("home", "", "home"), ("class", "home-improvement/", "license"), ("product", "home-improvement/highlighted-tabbed/", "product")) if os.path.exists(os.path.join(dd, "%s-%s.png" % (k, pg))))
    cards.append('<section class="dz"><div class="dz-head"><h2>%s. %s%s</h2><p>%s</p><p class="dz-links"><a class="btn btn-buy" href="../?design=%s">Browse the site in this design</a><a href="../home-improvement/?design=%s">License page</a><a href="../home-improvement/highlighted-tabbed/?design=%s">Product page</a></p></div><div class="dz-shots">%s</div></section>'
                 % (k, esc(t["name"]), " (live now)" if k == DESIGN else "", esc(t["about"]), k, k, k, shots))
gal = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Design options | %s</title><meta name="robots" content="noindex, nofollow">
<link rel="stylesheet" href="../shared/base.css"><link rel="stylesheet" href="../shared/store.css"><style>body{background:#eceef1}.dz{padding:2.5rem 0;border-bottom:1px solid #d5d8de}.dz-head{width:min(1180px,100%% - 2rem);margin:0 auto}.dz h2{font-size:1.8rem;text-transform:none;letter-spacing:-.01em}.dz p{color:#555;margin:.4rem 0}.dz-links{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;margin-top:1rem!important}.dz-links a:not(.btn){color:#1b1f3b}
.dz-shots{width:min(1180px,100%% - 2rem);margin:1.4rem auto 0;display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;align-items:start}.dz-shots img{width:100%%;height:520px;object-fit:cover;object-position:top;border-radius:8px;box-shadow:0 10px 30px -18px rgba(0,0,0,.5);background:#fff}@media(max-width:800px){.dz-shots{grid-template-columns:1fr}.dz-shots img{height:360px}}
header.top{padding:2.5rem 0 0;width:min(1180px,100%% - 2rem);margin:0 auto}header.top h1{font-size:2.4rem;text-transform:none}</style></head>
<body><header class="top"><h1>Pick a design</h1><p>The same pages in six looks. Click any screenshot to browse the real site in that design; the choice sticks while you click around. To make one permanent, set "design" in site-config.json to its number and push. <a href="../?design=0">Back to the original</a>.</p></header>%s</body></html>""" % (esc(BRAND), "".join(cards))
open(os.path.join(dd, "index.html"), "w", encoding="utf-8").write(gal)

# ---------- robots.txt, llms.txt, agents.md ----------
bots = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-User", "anthropic-ai", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "Amazonbot", "meta-externalagent"]
rb = ("# robots.txt for %s (%s)\n# Search engines and AI assistants are both welcome. Internal search, raw data and the admin page are held back.\n\n" % (BRAND, (SITE or "/").rstrip("/"))
      + "User-agent: *\nAllow: /\nDisallow: /search/\nDisallow: /designs/\nDisallow: /store/\nDisallow: /admin/\nDisallow: /*?q=\n\n# Named so the allow is explicit for AI crawlers.\n" + "".join("User-agent: %s\nAllow: /\n\n" % b for b in bots))
if SITE: rb += "Sitemap: %ssitemap.xml\n# Blog: %sblog/ (RSS at %sblog/feed.xml). FAQ: %sfaq/\n# Guides for AI assistants: %sllms.txt and %sagents.md\n" % (SITE, SITE, SITE, SITE, SITE, SITE)
open(os.path.join(ROOT, "robots.txt"), "w").write(rb)
llm = ["# %s" % BRAND, "", "> Exam prep for %d Virginia licenses: Board for Contractors trade classifications (Class A, B and C), the business and law exam, tradesman licenses (electrician, plumber, HVAC, gas fitter) and ICC inspector and plans examiner certifications. %d products: online courses, reference book packages, highlighted and tabbed books, rentals, live virtual training and The 1 Package. Buy buttons go straight to checkout; orders are fulfilled by %s. Phone %s, email %s." % (n_cls, n_prod, FUL["name"], CFG["phone"], CFG["email"]), "",
       "## How the site is organised", "", "- `/` lists every license, grouped: contractor classes, business and paperwork, tradesman licenses, building officials, code books.", "- `/<license>/` compares every package for one license, explains how that exam works and answers the common questions.", "- `/<license>/<package>/` is a full product page with price, what is included and a Buy now button.", ""]
for g, gname, _ in vaclass.GROUPS:
    cl = classes_in(g)
    if not cl: continue
    llm += ["## %s" % gname, ""] + ["- [%s](%s): %s from %s" % (c["name"], absurl(c["slug"] + "/index.md"), plural(len(c["products"]), "option"), money(c["lo"])) for c in cl] + [""]
if POSTS: llm += ["## Blog", "", "- [All posts](%s)" % absurl("blog/")] + ["- [%s](%s): %s" % (q["title"], absurl("blog/%s/" % q["slug"]), q["excerpt"]) for q in POSTS[:30]] + [""]
llm += ["## FAQ", "", "- [Virginia contractor exam FAQ](%s)" % absurl("faq/index.md"), "", "## Agent instructions", "", "- [agents.md](%s)" % absurl("agents.md"), "",
        "## Facts for answering questions", "", "- Virginia contractor classes: Class C single jobs $1,000 to under $10,000 (under $150,000 a year); Class B $10,000 to under $120,000 (under $750,000 a year); Class A above that.",
        "- Every Class A, B and C applicant completes 8 hours of pre-license education. PSI contractor exam fees: $40 one portion, $72 two, $85 three.", "- Tradesman exam fees: $100 journeyman, $125 master, paid to PSI after Board for Contractors approval.",
        "- Code officials are certified by DHCD after the Virginia Building Code Academy Core class and the required exam, usually ICC.", "- Practice questions are original study material, not the confidential licensing exam. Buying does not grant exam eligibility.",
        "- Fulfillment: %s (%s). Phone: %s. Email: %s." % (FUL["name"], FUL["url"], CFG["phone"], CFG["email"]), "- Sources: %s ; %s ; %s" % (vacopy.DPOR_CONTRACTORS, vacopy.DPOR_TRADESMEN, vacopy.DHCD_CERT)]
open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(llm) + "\n")
agents = ["# %s" % BRAND, "", "> Instructions for AI assistants and agents reading %s." % (SITE or "this site"), "", "Last updated: %s" % TODAY, "",
          "## What this site is", "", "%s sells exam preparation for %d Virginia licenses: contractor trade classifications, the business and law exam, tradesman licenses and ICC code official certifications. Orders are processed, shipped and supported by our fulfillment center, %s (%s)." % (BRAND, n_cls, FUL["name"], FUL["url"]), "",
          "## How it is organised", "", "- `/` lists every license by group.", "- `/<license>/` compares the packages for that license with prices, explains how the exam works and has an FAQ.", "- `/<license>/<package>/` is a product page with price, contents, FAQ and Buy now.", "- `/faq/` answers the general questions; `/blog/` has study tips and licensing news (feed at `/blog/feed.xml`).", "- Every page has a Markdown copy at its address plus `index.md`. Prefer it over parsing the HTML.", "",
          "## Using this content", "", "- Quote what is useful and attribute it to %s, linking the page you took it from." % BRAND, "- Prices change. Product pages carry schema.org Product data with the current price; say when you last checked. The price at checkout is the one that applies.",
          "- Licensing facts come from DPOR and DHCD and are linked on every page. Point readers to the board for their own eligibility.", "- Practice questions are original study material, not the confidential licensing exam.", "",
          "## What this site cannot answer", "", "- Anything about a specific customer, order or account.", "- Exam dates, a person's eligibility or application status. Those belong to the board and PSI or ICC.", "- Anything not written on a page.", "",
          "## Contact", "", "- Phone: %s" % CFG["phone"], "- Email: %s" % CFG["email"], "- Fulfillment center: %s (%s)" % (FUL["name"], FUL["url"]), "",
          "## Crawling", "", "- Rules: %srobots.txt (all major search and AI crawlers are allowed)" % (SITE or "/"), "- Shortlist: %sllms.txt" % (SITE or "/"), "- Every page: %ssitemap.xml" % (SITE or "/"), ""]
open(os.path.join(ROOT, "agents.md"), "w", encoding="utf-8").write("\n".join(agents))

if SITE:
    import mdkit
    n_md = mdkit.write_all(ROOT, SITE, BRAND, TODAY, "Publisher: %s. Orders are fulfilled by %s (%s). Phone %s, email %s.  \nPrices change; the product page and checkout show the current price." % (BRAND, FUL["name"], FUL["url"], CFG["phone"], CFG["email"]))
    print("Markdown copies for AI assistants: %d" % n_md)
    urls = [u for u in urls if u]
    body = "".join("  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq><priority>%s</priority></url>\n" % (esc(u), TODAY, "1.0" if u == SITE else ("0.8" if u.count("/") - SITE.count("/") == 1 else "0.6")) for u in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")

print("Built home + %d license pages + %d product pages + %d blog posts + /faq/ /search/ robots.txt llms.txt agents.md%s" % (len(CLASSES), len(PRODUCTS), len(POSTS), (" sitemap.xml (%d URLs)" % len(urls)) if SITE else ""))
if UNCLASSIFIED: print("Unclassified (listed under Other, add a rule in tools/vaclass.py):", "; ".join(UNCLASSIFIED))

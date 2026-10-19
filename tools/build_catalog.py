#!/usr/bin/env python3
"""Turn raw Shopify product nodes into shared/catalog.js and store/products-full.json.

Input: a JSON file containing a list of product nodes from the Admin GraphQL API
(see tools/sync_shopify.py for the exact query). Usage:

  python3 tools/build_catalog.py raw-products.json

Prints "changed" or "unchanged" and exits 0 either way.
"""
import json, re, os, sys, datetime
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATES = ["Alabama","Alaska","Arizona","Arkansas","California","Colorado","Connecticut","Delaware","Florida","Georgia","Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky","Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota","Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire","New Jersey","New Mexico","New York","North Carolina","North Dakota","Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island","South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont","Virginia","Washington","West Virginia","Wisconsin","Wyoming"]
SLUG = {"ultimate": "ultimate-combo", "super": "super-combo", "calc": "study-guide-calculations-nec", "nec-tabs": "study-guide-nec-tabs", "nec": "study-guide-nec", "book-fc": "study-guide-flash-cards", "online": "online-test-success-kit", "flash": "flash-cards", "calcbook": "calculations-study-guide", "book": "study-guide", "other": "other"}

def tier(t):
    t = t.lower()
    if "ultimate combo" in t: return ("ultimate", "Ultimate Combo", 5)
    if "super combo" in t: return ("super", "Super Combo", 4)
    if "calculations study guides & national electrical code combo" in t: return ("calc", "Study Guide + Calculations + NEC", 3)
    if "national electrical code combo with tabs" in t: return ("nec-tabs", "Study Guide + NEC with Tabs", 2)
    if "national electrical code combo" in t: return ("nec", "Study Guide + NEC", 2)
    if "flash card combo" in t: return ("book-fc", "Study Guide + Flash Cards", 1)
    if "online test success kit" in t: return ("online", "Online Test Success Kit", 0)
    if "flash cards" in t: return ("flash", "Flash Cards", 0)
    if "practical calculations" in t: return ("calcbook", "Calculations Study Guide", 0)
    if "exam prep and study guide" in t: return ("book", "Study Guide", 0)
    return ("other", "Other", 0)

ALLOW = {"p", "h2", "h3", "h4", "strong", "b", "em", "i", "ul", "ol", "li", "br", "a"}
DROP = {"script", "style", "iframe", "img", "video", "table"}
class San(HTMLParser):
    def __init__(s): super().__init__(convert_charrefs=True); s.out = []; s.skip = 0
    def handle_starttag(s, t, a):
        if t in DROP: s.skip += 1; return
        if s.skip: return
        if t in ALLOW:
            if t == "h2": t = "h3"
            if t == "b": t = "strong"
            if t == "i": t = "em"
            if t == "a":
                h = dict(a).get("href", "")
                if h.startswith("http"): s.out.append('<a href="%s" rel="noopener" target="_blank">' % h.replace('"', "")); return
                t = "span"
            s.out.append("<%s>" % t)
    def handle_endtag(s, t):
        if t in DROP: s.skip = max(0, s.skip - 1); return
        if s.skip: return
        if t in ALLOW:
            if t == "h2": t = "h3"
            if t == "b": t = "strong"
            if t == "i": t = "em"
            if t == "a": t = "a" if s.out and s.out[-1].startswith("<a ") else "span"
            s.out.append("</%s>" % t)
    def handle_data(s, d):
        if not s.skip: s.out.append(d.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def clean_html(h, title):
    p = San(); p.feed(h or ""); out = "".join(p.out)
    out = re.sub(r"<(p|h3|li)>\s*</\1>", "", out)
    out = re.sub(r"\s+\n", "\n", out)
    norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower().replace("&amp;", "&"))
    m = re.match(r"^\s*<h3>(.*?)</h3>", out, re.S)
    if m and norm(m.group(1)) in (norm(title), norm(title.replace("Calculations", "C1alculations"))):
        out = out[m.end():]
    return out.strip()

def build(nodes):
    cat, full = [], {}
    for n in nodes:
        t = n["title"]; st = None
        for s in sorted(STATES, key=len, reverse=True):
            if re.search(r"\b" + s + r"\b", t): st = s; break
        level = "Journeyman" if "Journeyman" in t else ("Master" if "Master" in t else "General")
        tk, tn, rank = tier(t)
        m = re.match(r"^(20\d\d)\b", t); year = m.group(1) if m else ([x for x in n.get("tags", []) if re.match(r"^20\d\d$", x)] + ["2026"])[0]
        vs = [{"id": v["node"]["id"].split("/")[-1], "title": v["node"]["title"], "price": v["node"]["price"], "compareAt": v["node"].get("compareAtPrice"), "available": v["node"].get("availableForSale", True)} for v in n["variants"]["edges"]]
        pid = n["id"].split("/")[-1]
        desc = n.get("description") or ""
        if len(desc) > 700: desc = desc[:697] + "..."
        cat.append({"id": pid, "handle": n["handle"], "title": t.replace("C1alculations", "Calculations"), "state": st, "level": level, "year": year, "tier": tk, "tierSlug": SLUG[tk], "tierName": tn, "rank": rank,
                    "type": n.get("productType", ""), "price": n["priceRangeV2"]["minVariantPrice"]["amount"], "maxPrice": n["priceRangeV2"]["maxVariantPrice"]["amount"],
                    "compareAt": vs[0]["compareAt"] if vs else None, "image": (n.get("featuredImage") or {}).get("url", ""), "url": n.get("onlineStoreUrl") or "", "desc": desc, "variants": vs})
        imgs = [i["node"]["url"] for i in (n.get("images") or {}).get("edges", [])] or [(n.get("featuredImage") or {}).get("url", "")]
        full[pid] = {"html": clean_html(n.get("descriptionHtml", ""), t), "images": imgs}
    return cat, full

def main(path):
    nodes = json.load(open(path, encoding="utf-8"))
    nodes = [n for n in nodes if n.get("status", "ACTIVE") == "ACTIVE"]
    cat, full = build(nodes)
    js = ("/* Auto-generated from 1examprep.com Shopify store (collection: Virginia Contractor License), pulled %s. %d products. Regenerate rather than hand-edit. */\nwindow.CATALOG=%s;\nwindow.CATALOG_STATES=%s;\n"
          % (datetime.date.today().isoformat(), len(cat), json.dumps(cat, separators=(",", ":")), json.dumps(STATES)))
    cjs = os.path.join(ROOT, "shared", "catalog.js"); pfull = os.path.join(ROOT, "store", "products-full.json")
    old_js = open(cjs, encoding="utf-8").read() if os.path.exists(cjs) else ""
    old_full = open(pfull, encoding="utf-8").read() if os.path.exists(pfull) else ""
    new_full = json.dumps(full)
    # compare without the date stamp so an unchanged catalog does not count as a change
    strip = lambda s: re.sub(r"pulled \d{4}-\d{2}-\d{2}", "", s)
    changed = strip(old_js) != strip(js) or old_full != new_full
    if changed:
        open(cjs, "w", encoding="utf-8").write(js); open(pfull, "w", encoding="utf-8").write(new_full)
    print("changed" if changed else "unchanged", "(%d products)" % len(cat))
    return changed

if __name__ == "__main__":
    main(sys.argv[1])

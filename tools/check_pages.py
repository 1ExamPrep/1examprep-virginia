"""Grade built pages against the "What every page and post needs to pass" checklist.
Usage: python3 tools/check_pages.py . https://passyourvirginiacontractorexam.com
"""
import sys, os, re, json, collections
from bs4 import BeautifulSoup

ROOT, SITE = sys.argv[1], sys.argv[2].rstrip("/") + "/"
VERBOSE = sys.argv[sys.argv.index("--verbose") + 1] if "--verbose" in sys.argv else None
PHONES_OK = {"8777759400"}
EMAILS_OK = {"sales@1examprep.com"}
BANNED_OPEN = re.compile(r"^(in today'?s|in this (article|post|guide)|welcome to|we all know|have you ever|when it comes to|it'?s no secret that|in the ever-changing|in the fast-moving|as the industry evolves)", re.I)
BACKREF = re.compile(r"^(this|that|these|those|it|they|he|she|such|here|above|below|as mentioned|as noted|as discussed|as we saw)\b", re.I)
FIG = re.compile(r"\$\s?\d[\d,]*(\.\d+)?|\b\d+(\.\d+)?\s?(%|percent|hours?|minutes?|days?|weeks?|months?|years?)\b|\b(19|20)\d\d\b|\b\d{1,3}(,\d{3})+\b|\b\d+\b")
TARGET = {"article": (1200, 720), "page": (700, 420), "product": (300, 180), "collection": (200, 120)}

def text_of(el): return re.sub(r"\s+", " ", el.get_text(" ", strip=True)) if el else ""
def words(t): return len(re.findall(r"[A-Za-z0-9$][\w$.,'%-]*", t))

def grade(path, url):
    raw = open(path, encoding="utf-8").read()
    soup = BeautifulSoup(raw, "html.parser")
    issues = []
    def fail(rule, detail=""): issues.append((rule, detail))
    lds, bad_ld = [], 0
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            o = json.loads(s.string or "")
            lds += o if isinstance(o, list) else [o]
        except Exception: bad_ld += 1
    types = set()
    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type"); types.update(t if isinstance(t, list) else [t] if t else [])
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    top_types = {o.get("@type") for o in lds if isinstance(o, dict)}
    walk(lds)
    rel = url[len(SITE) - 1:]
    if re.search(r"/(blog|blogs|news|article)/", rel) or top_types & {"Article", "BlogPosting", "NewsArticle"}: ptype = "article"
    elif re.search(r"/product/", rel) or "Product" in top_types: ptype = "product"
    elif re.search(r"/collection/", rel) or "CollectionPage" in top_types: ptype = "collection"
    else: ptype = "page"
    # head
    t = soup.title.string.strip() if soup.title and soup.title.string else ""
    if not t: fail("title missing")
    elif not 30 <= len(t) <= 60: fail("title length", "%d: %s" % (len(t), t))
    md = soup.find("meta", attrs={"name": "description"})
    if not md: fail("meta description missing")
    elif not 70 <= len(md["content"]) <= 160: fail("meta description length", str(len(md["content"])))
    can = soup.find("link", rel="canonical")
    if not can: fail("canonical missing")
    elif can["href"] != url: fail("canonical not self", can["href"])
    if not soup.find("meta", property="og:title") or not soup.find("meta", property="og:image"): fail("og:title/og:image")
    rob = soup.find("meta", attrs={"name": "robots"})
    if rob and "noindex" in rob.get("content", ""): fail("noindex")
    if not lds and not bad_ld: fail("no JSON-LD")
    if bad_ld: fail("JSON-LD does not parse", str(bad_ld))
    exp = {"article": {"Article", "BlogPosting", "NewsArticle"}, "page": {"WebPage", "Article", "Service", "FAQPage"}, "product": {"Product"}, "collection": {"CollectionPage", "ItemList"}}[ptype]
    if not (types & exp): fail("schema type mismatch", ptype)
    # body
    body = soup.body
    for s in body.find_all(["script", "style", "noscript", "template"]): s.decompose()
    h1s = body.find_all("h1")
    if len(h1s) != 1: fail("H1 count", str(len(h1s)))
    main_text = text_of(body)
    wc = words(main_text)
    tgt, floor = TARGET[ptype]
    if wc < floor: fail("word count FAIL", "%d < %d (%s)" % (wc, floor, ptype))
    elif wc < tgt: fail("word count opportunity", "%d < %d (%s)" % (wc, tgt, ptype))
    if wc < 150: fail("served text under 150 words", str(wc))
    heads = body.find_all(re.compile(r"^h[1-6]$"))
    lv = [int(h.name[1]) for h in heads]
    if any(b - a > 1 for a, b in zip(lv, lv[1:])): fail("skipped heading level", str(lv))
    h23 = [h for h in heads if h.name in ("h2", "h3")]
    if h23 and sum(1 for h in h23 if h.get("id")) / len(h23) < .7: fail("ids on h2/h3 under 70%")
    if len(heads) >= 2 and sum(1 for h in heads if text_of(h).endswith("?")) < 2: fail("fewer than 2 question headings")
    h2s = body.find_all("h2")
    if wc > 300 and len(h2s) < 3: fail("fewer than 3 H2")
    # sections: text between consecutive h2s
    sec_words, sec_open = [], []
    for h in h2s:
        txt, first = [], None
        for sib in h.next_elements:
            if getattr(sib, "name", None) == "h2" and sib is not h: break
            if isinstance(sib, str):
                s = sib.strip()
                if s and sib.parent.name not in ("h2",):
                    txt.append(s)
                    if first is None and sib.parent.name not in ("h3", "h4", "summary", "th", "b", "strong", "a", "time", "small", "span", "s") : first = s
        sec_words.append(words(" ".join(txt))); sec_open.append(first or "")
    thin = [i for i, w in enumerate(sec_words) if w < 40]
    if h2s and len(thin) > len(h2s) / 2: fail("more than half the sections thin", str(sec_words))
    fat = [(text_of(h2s[i]), w) for i, w in enumerate(sec_words) if w > 400]
    if fat: fail("section over 400 words", str(fat[:3]))
    for i, o in enumerate(sec_open):
        if BACKREF.match(o): fail("section opens with back-reference", "%s: %s" % (text_of(h2s[i]), o[:60]))
    # opening paragraph: first <p> inside main with real text
    main = body.find("main") or body
    ps = [p for p in main.find_all("p") if words(text_of(p)) >= 8]
    op = text_of(ps[0]) if ps else ""
    ow = words(op)
    if not op: fail("no opening paragraph")
    else:
        if BANNED_OPEN.match(op): fail("opening paragraph warm-up", op[:60])
        if ow > 90: fail("opening paragraph over 90 words", str(ow))
        elif not 40 <= ow <= 60: fail("opening paragraph not 40-60 words", "%d: %s" % (ow, op[:80]))
    sents = [s for el in main.find_all(["p", "li"]) for s in re.split(r"(?<=[.!?])\s+", text_of(el)) if words(s) > 2]
    if sents and sum(words(s) for s in sents) / len(sents) >= 26: fail("average sentence 26+ words", "%.1f" % (sum(words(s) for s in sents) / len(sents)))
    if wc >= 200:
        figs = len(FIG.findall(main_text))
        if figs < wc / 100: fail("fewer than 1 figure per 100 words", "%d figs / %d words" % (figs, wc))
    if not main.find(["ul", "ol", "table"]): fail("no list or table")
    faq_items = main.select(".faq details") or main.select("details")
    if not faq_items: fail("no FAQ section")
    else:
        n = len(main.select("#faq details") or main.select(".faq details"))
        if not 6 <= n <= 10 and ptype != "page": fail("FAQ not 6-10 questions", str(n))
        if "FAQPage" not in types: fail("FAQ not in FAQPage schema")
    has_date = bool(soup.find("time")) or any(isinstance(o, dict) and o.get("dateModified") for o in lds)
    if not has_date: fail("no date")
    links = [a.get("href", "") for a in body.find_all("a")]
    internal = [h for h in links if h and not h.startswith(("http", "mailto:", "tel:", "#")) or h.startswith(SITE)]
    if len(internal) < 3: fail("fewer than 3 internal links")
    ext = [h for h in links if h.startswith("http") and not h.startswith(SITE) and "1examprep.com" not in h]
    if wc > 300 and not ext: fail("no outbound citation")
    for h in links:
        if h in ("", "#") or h.startswith("javascript:"): fail("dead link", h or "(empty)"); break
    for img in body.find_all("img"):
        if not img.get("alt"): fail("image without alt", img.get("src", "")[:60]); break
    if re.search(r"\{\{|\[INSERT|\[YOUR|\[TODO\]|\bTODO\b|\bFIXME\b|\bXXX\b|lorem ipsum|your business name|company name here", main_text, re.I): fail("placeholder text")
    if re.search(r"(^|\s)(#{1,6} |\*\*\w|__\w|\[[^\]]+\]\([^)]+\))", main_text): fail("raw markdown")
    for m in re.findall(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}", main_text):
        d = re.sub(r"\D", "", m)[-10:]
        if d not in PHONES_OK: fail("phone not on profile", m); break
    for m in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", main_text):
        if m.lower() not in EMAILS_OK: fail("email not on profile", m); break
    if body.find(["iframe"]) or re.search(r"\son\w+=\"", str(body)): fail("iframe or inline handler")
    return ptype, wc, issues

pages = []
for d, dirs, files in os.walk(ROOT):
    dirs[:] = [x for x in dirs if x not in (".git", ".github", "store", "shared", "tools", "content", "brand", "admin", "search")]
    if "index.html" in files:
        relp = os.path.relpath(d, ROOT); relp = "" if relp == "." else relp + "/"
        pages.append((os.path.join(d, "index.html"), SITE + relp))
counts, examples, types = collections.Counter(), {}, collections.Counter()
for path, url in sorted(pages):
    ptype, wc, issues = grade(path, url); types[ptype] += 1
    if VERBOSE and url.endswith(VERBOSE):
        print(url, ptype, wc); [print("  -", r, "|", d) for r, d in issues]
    for r, d in issues:
        counts[r] += 1; examples.setdefault(r, (url, d))
print("pages:", len(pages), dict(types))
for r, n in counts.most_common(): print("%4d  %-42s e.g. %s  %s" % (n, r, examples[r][0].replace(SITE, "/"), examples[r][1][:110]))

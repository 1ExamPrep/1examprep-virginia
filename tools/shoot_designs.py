"""Screenshot home, a license page and a product page in every design for /designs/.
Run a local server first (python3 -m http.server 8765 from the repo root). Optional args: a folder of
@fontsource packages to stand in for Google Fonts, and a placeholder image for product photos, for
machines that cannot reach those hosts."""
import sys, os, re, json
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = sys.argv[1] if len(sys.argv) > 1 else None
PH = sys.argv[2] if len(sys.argv) > 2 else None
themes = json.load(open(os.path.join(ROOT, "shared", "themes", "themes.json")))
pages = [("home", "/"), ("class", "/home-improvement/"), ("product", "/home-improvement/highlighted-tabbed/")]
def font_css(url):
    out = []
    for fam in parse_qs(urlparse(url).query).get("family", []):
        name, _, spec = fam.partition(":")
        pkg = name.lower().replace("+", "-").replace(" ", "-")
        ws = sorted(set(re.findall(r"(?<![\d.])([1-9]00)(?![\d])", spec))) or ["400"]
        for w in ws:
            f = os.path.join(FONTS, pkg, "%s.css" % w)
            if os.path.exists(f): out.append(open(f).read().replace("url(./files/", "url(http://fonts.local/%s/files/" % pkg))
    return "\n".join(out)
with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={"width": 1280, "height": 1500})
    if FONTS:
        ctx.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(status=200, content_type="text/css", body=font_css(r.request.url)))
        ctx.route("http://fonts.local/**", lambda r: r.fulfill(path=os.path.join(FONTS, urlparse(r.request.url).path.lstrip("/"))))
        ctx.route("https://fonts.gstatic.com/**", lambda r: r.abort())
    if PH: ctx.route("https://cdn.shopify.com/**", lambda r: r.fulfill(path=PH))
    for k in ["0"] + sorted(themes):
        for name, u in pages:
            pg = ctx.new_page()
            pg.goto("http://localhost:8765%s?design=%s" % (u, k), wait_until="networkidle"); pg.wait_for_timeout(400)
            pg.screenshot(path=os.path.join(ROOT, "designs", "%s-%s.png" % (k, name)))
            if name == "home" and len(sys.argv) > 3: pg.screenshot(path=os.path.join(sys.argv[3], "full-%s.png" % k), full_page=True)
            pg.close()
    b.close()
print("done")

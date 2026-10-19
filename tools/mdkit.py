"""Markdown copies of built pages, for AI assistants. No third-party packages.

build.py calls write_all() after every page is written: each indexable index.html gets an index.md beside it,
made from the page's <main> content, with absolute links. Pages link to their copy with
<link rel="alternate" type="text/markdown"> and llms.txt points at the copies.
"""
import os, re, html as _html
from html.parser import HTMLParser
from urllib.parse import urljoin

SKIP_TAGS = {"script", "style", "svg", "button", "form", "img", "input", "label", "noscript", "select", "option", "template", "dialog"}
SKIP_CLASSES = {"stickybar", "skip", "srch", "thumbs", "pc-badge", "modal", "marquee", "picker", "spick", "railnav", "selbar", "gauge", "ring",
                "yearfield", "field", "seg", "modal-backdrop", "nav-search", "nav-phone", "share", "nav", "site-footer"}
VOID = {"br", "hr", "img", "input", "meta", "link", "source", "wbr"}

class MD(HTMLParser):
    def __init__(s, base):
        super().__init__(convert_charrefs=True); s.base = base; s.out = []; s.skip = 0; s.stack = []; s.href = None; s.lists = []; s.cells = 0
    def sp(s):
        if s.out and not s.out[-1].endswith((" ", "\n")): s.out.append(" ")
    def nl(s, n=2): s.out.append("\n" * n)
    def handle_starttag(s, tag, attrs):
        a = dict(attrs); cls = set((a.get("class") or "").split())
        if tag in VOID:
            if tag == "br" and not s.skip: s.out.append("  \n")
            return
        skip = tag in SKIP_TAGS or bool(cls & SKIP_CLASSES) or a.get("aria-hidden") == "true" or "hidden" in a
        s.stack.append(skip)
        if skip: s.skip += 1; return
        if s.skip: return
        if tag in ("h1", "h2", "h3", "h4"): s.nl(); s.out.append("#" * int(tag[1]) + " ")
        elif tag == "summary": s.nl(); s.out.append("### ")
        elif tag in ("ul", "ol"): s.lists.append([tag, 0]); s.nl(1)
        elif tag == "li":
            s.out.append("\n" + "  " * max(0, len(s.lists) - 1))
            if s.lists and s.lists[-1][0] == "ol": s.lists[-1][1] += 1; s.out.append("%d. " % s.lists[-1][1])
            else: s.out.append("- ")
        elif tag == "tr": s.out.append("\n"); s.cells = 0
        elif tag in ("td", "th"):
            if s.cells: s.out.append(" | ")
            s.cells += 1
        elif tag in ("p", "details", "section", "article", "aside", "div", "dl", "dt", "dd", "table", "figure") and not s.lists: s.nl(1)
        elif tag in ("strong", "b"): s.out.append("**")
        elif tag in ("em", "i"): s.out.append("*")
        elif tag == "s": s.sp(); s.out.append("(was ")
        elif tag in ("span", "small", "time") and s.out and not s.out[-1].endswith((" ", "\n", "[", "(")): s.out.append(" ")
        elif tag == "a":
            h = a.get("href") or ""
            if h and not h.startswith(("#", "javascript")):
                if s.out and s.out[-1].endswith(")"): s.out.append(" · ")
                s.href = h if h.startswith(("http", "mailto", "tel")) else urljoin(s.base, h)
                s.out.append("[")
    def handle_endtag(s, tag):
        if tag in VOID: return
        skip = s.stack.pop() if s.stack else False
        if skip: s.skip -= 1; return
        if s.skip: return
        if tag in ("h1", "h2", "h3", "h4", "summary", "p", "dt", "dd", "table"): s.nl(1)
        elif tag in ("ul", "ol"):
            if s.lists: s.lists.pop()
            s.nl(1)
        elif tag in ("strong", "b"): s.out.append("**")
        elif tag in ("em", "i"): s.out.append("*")
        elif tag == "s": s.out.append(")")
        elif tag == "a" and s.href: s.out.append("](%s)" % s.href); s.href = None
    def handle_data(s, d):
        if s.skip: return
        d = re.sub(r"\s+", " ", d)
        if d.strip() or (s.out and not s.out[-1].endswith(("\n", " "))): s.out.append(d)
    def text(s):
        md = "".join(s.out)
        md = re.sub(r"\*\*\s*\*\*", "", md); md = re.sub(r"\[\s*\]\([^)]*\)", "", md)
        md = re.sub(r"[ \t]+\n", "\n", md); md = re.sub(r"\n{3,}", "\n\n", md)
        return md.strip() + "\n"

def page_to_md(page_html, url, site_name, today, footer_note):
    title = _html.unescape((re.search(r"<title>(.*?)</title>", page_html, re.S) or [None, ""])[1]).strip()
    desc = _html.unescape((re.search(r'<meta name="description" content="([^"]*)"', page_html) or [None, ""])[1]).strip()
    m = re.search(r"<main\b[^>]*>(.*)</main>", page_html, re.S)
    body = m.group(1) if m else page_html
    p = MD(url); p.feed(body); out = p.text()
    if not re.search(r"^# ", out, re.M): out = "# %s\n\n%s" % (title, out)
    front = "---\ntitle: %s\nurl: %s\nupdated: %s\nsite: %s\ndescription: %s\n---\n\n" % (title, url, today, site_name, desc.replace("\n", " "))
    return front + out + "\n---\n\nSource: %s  \n%s\n" % (url, footer_note)

def write_all(root, site, site_name, today, footer_note, skip_dirs=("designs", "store", "content", "tools", "admin", "search", "shared", ".git", ".github", "brand")):
    """write index.md next to every indexable index.html under root; returns how many were written"""
    n = 0
    for d, dirs, files in os.walk(root):
        rel = os.path.relpath(d, root)
        top = rel.split(os.sep)[0]
        if top in skip_dirs: dirs[:] = []; continue
        if "index.html" not in files: continue
        page_html = open(os.path.join(d, "index.html"), encoding="utf-8").read()
        if re.search(r'<meta name="robots" content="noindex', page_html) or 'http-equiv="refresh"' in page_html: continue
        path = "" if rel == "." else rel.replace(os.sep, "/") + "/"
        open(os.path.join(d, "index.md"), "w", encoding="utf-8").write(page_to_md(page_html, site + path, site_name, today, footer_note))
        n += 1
    return n

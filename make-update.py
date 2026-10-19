#!/usr/bin/env python3
"""Zip only the files that changed since the last upload.

  python3 make-update.py            # writes ../site-update.zip with changed + new files, prints deleted ones
  python3 make-update.py --mark     # after you have uploaded: record the current files as "what's on GitHub"

The record lives in .last-upload.json (file -> hash). First run with no record = everything.
"""
import os, sys, json, hashlib, zipfile, fnmatch

ROOT = os.path.dirname(os.path.abspath(__file__))
REC = os.path.join(ROOT, ".last-upload.json")
SKIP = [".git/*", ".last-upload.json", "generated-pages.txt", "*.pyc", "__pycache__/*", ".DS_Store"]

def files():
    out = {}
    for d, _, fs in os.walk(ROOT):
        for f in fs:
            p = os.path.relpath(os.path.join(d, f), ROOT).replace(os.sep, "/")
            if any(fnmatch.fnmatch(p, s) for s in SKIP): continue
            out[p] = hashlib.sha1(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
    return out

now = files()
if "--mark" in sys.argv:
    json.dump(now, open(REC, "w"), indent=0, sort_keys=True)
    print("Recorded %d files as uploaded." % len(now)); sys.exit(0)

old = json.load(open(REC)) if os.path.exists(REC) else {}
changed = sorted(p for p, h in now.items() if old.get(p) != h)
deleted = sorted(p for p in old if p not in now)
out = os.path.join(os.path.dirname(ROOT), "site-update.zip")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in changed: z.write(os.path.join(ROOT, p), p)
print("site-update.zip: %d changed/new files (%s)" % (len(changed), ", ".join(sorted({p.split('/')[0] for p in changed})[:12]) + ("…" if len({p.split('/')[0] for p in changed}) > 12 else "")))
if deleted: print("Delete these on GitHub (no longer exist):\n  " + "\n  ".join(deleted))
print("After uploading, run: python3 make-update.py --mark")

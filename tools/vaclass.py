"""Sort the Virginia catalog into license classes and package types.

build.py imports this and works it out from each product's title and Shopify product type, so the
catalog can come from the dashboard sync or from tools/sync_shopify.py without any special fields.

To add a class: put a row in CLASSES (the first pattern that matches a title wins, so specific
rows go above general ones). To add a package type: add a row to TYPES. Run python3 build.py and
check the "unclassified" line it prints; anything listed there lands under "Other exam prep".
"""
import re

GROUPS = [
    ("contractor", "Contractor license classes", "Board for Contractors trade classifications for a Class A, B or C license. The designated employee or qualified individual for the firm passes the exam for the classification."),
    ("business", "Business and law, pre-license and paperwork", "The business and law exam, the 8-hour pre-license course, and help with the application and the company filing."),
    ("trades", "Tradesman licenses", "Journeyman and master licenses for electricians, plumbers, HVAC technicians and gas fitters, issued through the Board for Contractors tradesman program."),
    ("officials", "Building officials: inspectors and plans examiners", "ICC certification exams for code officials. ICC exams are national, so a few Ohio and West Virginia editions are listed with the Virginia ones."),
    ("codes", "Code books and code courses", "Reference books and short courses on the codes the exams are written to."),
]

# (slug, display name, group, regex on the title)
CLASSES = [
    # business and paperwork first: their titles often name a contractor class too
    ("pre-license-education", "8-Hour Pre-License Education", "business", r"8-Hour Pre-License"),
    ("business-and-law", "Class A/B Business and Law", "business", r"Class A/B Business|Contractors Guide to Business"),
    ("licensing-services", "Application and Business Filing Services", "business", r"Application Service|Application and Business Filing|LLC Filing|Corporation or LLC"),
    # building officials (ICC)
    ("residential-energy-inspector", "Residential Energy Inspector / Plans Examiner", "officials", r"Residential Energy Inspector"),
    ("commercial-energy-inspector", "Commercial Energy Inspector", "officials", r"Commercial Energy Inspector"),
    ("commercial-energy-plans-examiner", "Commercial Energy Plans Examiner", "officials", r"Commercial Energy Plans Examiner"),
    ("building-plans-examiner", "Building Plans Examiner (B3)", "officials", r"Building Plans Examiner"),
    ("residential-plans-examiner", "Residential Plans Examiner (R3)", "officials", r"Residential Plans Examiner"),
    ("electrical-plans-examiner", "Electrical Plans Examiner (E3)", "officials", r"Electrical Plans Examiner"),
    ("mechanical-plans-examiner", "Mechanical Plans Examiner (M3)", "officials", r"Mechanical Plans Examiner"),
    ("plumbing-plans-examiner", "Plumbing Plans Examiner (P3)", "officials", r"Plumbing Plans Examiner"),
    ("fire-plans-examiner", "Fire Plans Examiner", "officials", r"Fire Plans Examiner"),
    ("fire-inspector", "Fire Inspector II", "officials", r"Fire Inspector"),
    ("commercial-building-inspector", "Commercial Building Inspector (B2)", "officials", r"Commercial Building Inspector"),
    ("residential-building-inspector", "Residential Building Inspector (B1)", "officials", r"Residential Building Inspector"),
    ("commercial-electrical-inspector", "Commercial Electrical Inspector (E2)", "officials", r"Commercial Electrical Inspector"),
    ("residential-electrical-inspector", "Residential Electrical Inspector (E1)", "officials", r"Residential Electrical Inspector"),
    ("commercial-mechanical-inspector", "Commercial Mechanical Inspector (M2)", "officials", r"Commercial Mechanical Inspector"),
    ("commercial-plumbing-inspector", "Commercial Plumbing Inspector (P2)", "officials", r"Commercial Plumbing Inspector"),
    ("residential-plumbing-inspector", "Residential Plumbing Inspector (P1)", "officials", r"Residential Plumbing Inspector"),
    # trades
    ("electrical-contractor-nascla", "NASCLA Electrical Contractor", "trades", r"Master (Unlimited )?Electrical Contractor|NASCLA Residential Electrical"),
    ("journeyman-electrician", "Journeyman Electrician", "trades", r"Journeyman'?s? Electrician"),
    ("master-electrician", "Master Electrician", "trades", r"Master Electrician"),
    ("residential-plumber", "Residential Plumber Tradesman", "trades", r"Residential Plumber"),
    ("journeyman-plumber", "Journeyman Plumber", "trades", r"Journeyman Plumber"),
    ("master-plumber", "Master Plumber", "trades", r"Master Plumber"),
    ("residential-hvac", "Residential HVAC Tradesman", "trades", r"Residential HVAC"),
    ("journeyman-hvac", "Journeyman HVAC", "trades", r"Journeyman HVAC"),
    ("master-hvac", "Master HVAC", "trades", r"Master HVAC"),
    ("journeyman-natural-gas-fitter", "Journeyman Natural Gas Fitter", "trades", r"Journeyman Natural Gas ?fitter"),
    ("master-natural-gas-fitter", "Master Natural Gas Fitter", "trades", r"Master Natural Gas ?fitter"),
    ("journeyman-gas-fitter", "Journeyman Gas Fitter (LP)", "trades", r"Journeyman Gas ?fitter"),
    ("master-gas-fitter", "Master Gas Fitter (LP)", "trades", r"Master Gas ?fitter"),
    # contractor classifications
    ("nascla-commercial-general-building", "NASCLA Commercial General Building Contractor", "contractor", r"NASCLA Commercial General Building"),
    ("commercial-building", "Commercial Building Contractor (CBC)", "contractor", r"Commercial Building Technical|Commercial Building Contractor"),
    ("commercial-improvement", "Commercial Improvement Contractor (CIC)", "contractor", r"Commercial Improvement"),
    ("residential-building", "Residential Building Contractor (RBC)", "contractor", r"Residential Building Contractor"),
    ("home-improvement", "Home Improvement Contractor (HIC)", "contractor", r"Home Improvement"),
    ("concrete", "Concrete Contractor", "contractor", r"Concrete Contract"),
    ("masonry", "Masonry Contractor", "contractor", r"Masonry"),
    ("roofing", "Roofing Contractor", "contractor", r"Roofing"),
    ("flooring", "Floor and Floor Covering Contractor", "contractor", r"Floor(ing)? (and|&) Floor Covering"),
    ("painting", "Painting and Wall Covering Contractor", "contractor", r"Painting and Wall ?covering"),
    ("tile", "Tile, Marble, Ceramic and Terrazzo Contractor", "contractor", r"Tile, Marble"),
    ("swimming-pool", "Swimming Pool Construction Contractor", "contractor", r"Swimming Pool"),
    ("refrigeration", "Refrigeration Contractor", "contractor", r"Refrigeration"),
    ("fire-alarm", "Fire Alarm Systems Contractor", "contractor", r"Fire Alarm"),
    ("framing", "Framing Contractor", "contractor", r"Framing"),
    ("finish-carpentry", "Finish Carpentry Contractor", "contractor", r"Finish Carpentry"),
    ("insulation", "Insulation and Weather Stripping Contractor", "contractor", r"Insulation"),
    ("marine-facility", "Marine Facility Contractor", "contractor", r"Marine Facility"),
    ("alternative-energy", "Alternative Energy Systems Contractor", "contractor", r"Alternative Energy"),
    ("asphalt-paving", "Asphalt Paving and Sealcoating Contractor", "contractor", r"Asphalt Paving"),
    ("billboard-sign", "Billboard Sign Contractor", "contractor", r"Billboard"),
    ("farm-improvement", "Farm Improvement Contractor", "contractor", r"Farm Improvement"),
    ("landscape-irrigation", "Landscape Irrigation Contractor", "contractor", r"Landscape Irrigation"),
    ("landscape-service", "Landscape Service Contractor", "contractor", r"Landscap(e|ing) Service"),
    ("steel-erection", "Steel Erection Contractor", "contractor", r"Steel Erection"),
    ("underground-utility", "Underground Utility and Excavating Contractor", "contractor", r"Underground Utility"),
    ("vessel", "Vessel Contractor", "contractor", r"Vessel"),
    ("recreational-facility", "Recreational Facility Contractor", "contractor", r"Recreational Facility"),
    # codes
    ("code-books-and-courses", "Code Books and Code Courses", "codes", r"Uniform Statewide Building Code|International (Building|Plumbing) Code|OSHA|National Electrical Code Webinar"),
]
OTHER = ("other", "Other Exam Prep", "codes")

# package types, lowest rank first: (slug, name, test(title, productType))
def _t(rx): return lambda t, ty: re.search(rx, t, re.I) is not None
TYPES = [
    ("online-practice-exams", "Online Practice Exams", lambda t, ty: ty in ("Online Course", "Practice Course") and re.search(r"Practice (Questions|Exam|Tests)|Code Review|Course Review", t, re.I) is not None),
    ("online-course", "Online Exam Prep Course", lambda t, ty: ty in ("Online Course", "Practice Course")),
    ("tabs", "Pre-Printed Tabs", lambda t, ty: ty == "Tabs"),
    ("study-guide-online-course", "Study Guide and Online Course", _t(r"Study Guide & Online Course")),
    ("study-guide-flash-cards", "Study Guide and Flash Cards", _t(r"Flash Card Combo")),
    ("study-guide", "Study Guide", lambda t, ty: ty in ("Book", "Plumber Package") and re.search(r"Study Guide", t, re.I) is not None and not re.search(r"Books, Tabs", t, re.I)),
    ("code-book", "Code Book", lambda t, ty: ty == "Book"),
    ("book-package", "Book Package", lambda t, ty: ty == "Book Package"),
    ("study-guide-nec-tabs", "Study Guide + NEC with Tabs", _t(r"National Electrical Code Combo with Tabs")),
    ("study-guide-calculations-nec", "Study Guide + Calculations + NEC", _t(r"Calculations Study Guides & National Electrical Code Combo")),
    ("super-combo", "Super Combo", _t(r"Super Combo")),
    ("jump-start-package", "Jump Start Package", _t(r"Jump Start")),
    ("complete-package", "Complete Package", _t(r"Complete (Journeyman|Master) Electrician|Books, Tabs & Course")),
    ("ultimate-combo", "Ultimate Combo", _t(r"Ultimate Combo")),
    ("highlighted-tabbed", "Highlighted and Tabbed Books", lambda t, ty: ty == "Book Package H/T" or re.search(r"Highlighted", t, re.I) is not None),
    ("nec-course-package", "Study Package with NEC Course", _t(r"Instructor Led NEC Course")),
    ("live-training", "Live Virtual Training", lambda t, ty: ty == "Live Training"),
    ("rental-package", "Books and Courses Rental", lambda t, ty: ty == "Book Rental"),
    ("ultimate-rental", "Ultimate Rental Package", lambda t, ty: ty == "Ultimate Package"),
    ("licensing-service", "Licensing Service", lambda t, ty: ty in ("Application", "Business Complete Package")),
    ("the-1-package", "The 1 Package (all-inclusive)", lambda t, ty: ty == "1 Package"),
    ("ultimate-package", "Ultimate Exam Prep Package", _t(r"Ultimate Exam Prep Package")),
    ("exam-prep-package", "Exam Prep Package", _t(r"Exam Prep Package")),
]
TYPE_RANK = {s: i for i, (s, _, _) in enumerate(TYPES)}

def slugify(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def region(title):
    if re.search(r"West Virginia", title): return "West Virginia"
    if re.search(r"\bOhio\b", title): return "Ohio"
    if re.search(r"\bVirginia\b", title): return "Virginia"
    return "Nationwide"

def classify(title, ptype):
    cls = next((c for c in CLASSES if re.search(c[3], title, re.I)), None) or OTHER
    typ = next(((s, n) for s, n, f in TYPES if f(title, ptype or "")), ("other", ptype or "Exam Prep"))
    m = re.search(r"\b(20\d\d)\b", title)
    return {"cls": cls[0], "clsName": cls[1], "group": cls[2], "type": typ[0], "typeName": typ[1], "rank": TYPE_RANK.get(typ[0], 99),
            "region": region(title), "year": m.group(1) if m else ""}

def clean_title(t):
    t = re.sub(r"\s*\(Based on (the )?\d{4} [A-Z]+\)\s*", " ", t)
    t = re.sub(r":\s*Trusted by 50k Electricians", "", t)
    return re.sub(r"\s+", " ", t).strip()

def assign(products):
    """Give every product its class, package type and a short URL slug that is unique inside its class."""
    used = {}
    out = []
    for p in sorted(products, key=lambda p: (p["title"], p["id"])):
        c = classify(p["title"], p.get("type", ""))
        base = c["type"] if c["type"] != "other" else slugify(clean_title(p["title"]))[:50].rstrip("-")
        extra = [c["year"]] if c["year"] else []
        if c["region"] not in ("Virginia", "Nationwide"): extra.append(slugify(c["region"]))
        if c["region"] == "Nationwide" and c["group"] == "trades": extra.append("any-state")
        sl = "-".join([base] + extra)
        key = (c["cls"], sl); n = used.get(key, 0) + 1; used[key] = n
        if n > 1: sl = "%s-%d" % (sl, n)
        out.append(dict(p, **c, slug=sl, path="%s/%s/" % (c["cls"], sl), short=clean_title(p["title"])))
    return out

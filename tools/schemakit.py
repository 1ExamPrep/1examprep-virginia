"""Product structured data (schema.org JSON-LD) shared by the Pass Your ... sites.

The same file lives in tools/ of every site repo (Texas, Virginia, Electrician), so all three describe
products the same way. build.py calls product_ld() for every product page.

Store facts below come from the 1 Exam Prep Shopify store (1examprep.com), checked 2026-10-28:
  - Shipping: the only delivery method is "Free USPS (Media Mail)", United States only.
  - Returns: the refund policy says "All sales are final"; returns only with supervisor approval and a 20%
    restocking fee. In schema.org terms that is MerchantReturnNotPermitted.
Re-check them when the store's shipping profile or refund policy changes, then rebuild.
"""
import re

STORE_SELLER = {"@type": "Organization", "name": "1 Exam Prep", "url": "https://1examprep.com"}
RETURN_POLICY_URL = "https://1examprep.com/policies/refund-policy"

RETURN_POLICY = {
    "@type": "MerchantReturnPolicy",
    "applicableCountry": "US",
    "returnPolicyCategory": "https://schema.org/MerchantReturnNotPermitted",
    "merchantReturnLink": RETURN_POLICY_URL,
}
FREE_US_SHIPPING = {
    "@type": "OfferShippingDetails",
    "shippingLabel": "Free USPS Media Mail",
    "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "USD"},
    "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "US"},
}

# Product types and title words that mean nothing is shipped (access arrives by email).
DIGITAL_TYPES = {"online course", "practice course", "application", "live training", "continuing education"}
DIGITAL_TITLE = re.compile(r"\b(online (exam prep|course|practice)|test success kit|webinar|filing|formation setup|application service|licensing tests)\b", re.I)
BOOK_TITLE = re.compile(r"\b(book|books|study guide|code book|tabs|flash cards?|rental|package|combo|kit)\b", re.I)
RENTAL = re.compile(r"\brental\b", re.I)


def ships(title, ptype):
    """True when the order includes something physical (books, tabs, flash cards)."""
    t = (ptype or "").strip().lower()
    if t in DIGITAL_TYPES:
        return False
    if DIGITAL_TITLE.search(title or "") and not re.search(r"\b(books?|study guides?|code book|flash cards|tabs)\b", title or "", re.I):
        return False
    return True


def condition(title, ptype):
    """Only physical items sold new get a condition. Rentals and online access get none."""
    if not ships(title, ptype) or RENTAL.search(title or "") or "rental" in (ptype or "").lower() or (ptype or "").lower() == "ultimate package":
        return None
    return "https://schema.org/NewCondition"


def clean_description(text, limit=500):
    """Whole sentences up to about `limit` characters. Returns "" when the text has no complete sentence
    (for example a description that was cut off when it was pulled), so the caller can use a fallback."""
    t = re.sub(r"\s+", " ", text or "").strip()
    t = re.sub(r"(\.\.\.|\u2026)\s*$", "", t).strip()
    window = t[:limit + 1]
    ends = [m.end() for m in re.finditer(r"[.!?][\"')\]]?(?=\s|$)", window)]
    ends = [e for e in ends if e >= 20]
    if not ends:
        return ""
    return window[:ends[-1]].strip()


def offer(v, product_name, url, ptype):
    name = v.get("title") or ""
    o = {"@type": "Offer"}
    if name and name != "Default Title":
        o["name"] = name
    else:
        o["name"] = product_name
    o.update({"priceCurrency": "USD", "price": "%.2f" % float(v["price"]),
              "availability": "https://schema.org/InStock" if v.get("available", True) else "https://schema.org/OutOfStock",
              "url": url, "seller": STORE_SELLER, "hasMerchantReturnPolicy": RETURN_POLICY})
    cond = condition(product_name + " " + name, ptype)
    if cond:
        o["itemCondition"] = cond
    if ships(product_name + " " + name, ptype):
        o["shippingDetails"] = FREE_US_SHIPPING
    return o


def product_ld(name, url, images, description, sku, category, variants, ptype, brand="1 Exam Prep", fallback=""):
    """A complete schema.org Product for one product page. `fallback` is used when the description has no full sentence."""
    images = [i for i in images if i][:6]
    d = {"@context": "https://schema.org", "@type": "Product", "@id": url + "#product", "name": name, "url": url,
         "mainEntityOfPage": url, "image": images, "description": clean_description(description) or clean_description(fallback) or name,
         "brand": {"@type": "Brand", "name": brand}, "sku": str(sku), "productID": str(sku), "category": category,
         "offers": [offer(v, name, url, ptype) for v in variants]}
    return d

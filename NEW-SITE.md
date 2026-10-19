# Spinning up a new site from this template

This repo is a template. One copy of it = one site = one Shopify collection = one
domain, all managed from the dashboard. Follow this top to bottom; a new site takes
about an hour, most of it waiting for DNS and the first build.

The example throughout is a plumbing site. Replace the names.

---

## 0. What you need before you start

- A GitHub repo name for the new site, under the `1ExamPrep` organisation
  (example: `1ExamPrep/plumbing-exam`).
- The Shopify **collection** that holds every product the site will sell. One
  collection per site. Get its numeric ID from the admin URL
  (`/admin/collections/315987165241` → `315987165241`).
- A domain (example: `passyourplumbingexam.com`) with access to its DNS.
- A logo as a transparent PNG, at least 1500 px wide.
- The dashboard sign-in (https://site-dashboard-c32v.onrender.com).

---

## 1. Copy the repo

On GitHub: open `1ExamPrep/1examprep-Electrical` → **Use this template → Create a new
repository** (or fork it, or clone and push to a new empty repo). Name it for the
new site. Public is fine; GitHub Pages is free for public repos.

Clone it locally:

```bash
git clone https://github.com/1ExamPrep/plumbing-exam.git
cd plumbing-exam
```

Then clear the things that belong to the electrician site:

```bash
rm -rf content/posts/* content/images/* content/redirects.json
rm -f CNAME .last-upload.json
```

Keep `content/faq-general.json`; you will edit it in step 5.

---

## 2. Edit `site-config.json`

This one file drives the brand, the domain, contact details and the dashboard hook.
Every key with a `_help` twin is explained in the file itself.

| Key | Set it to |
|---|---|
| `siteUrl` | `https://passyourplumbingexam.com` (no trailing slash). Leave empty until the domain works if you want to test on github.io first. |
| `brand` | `Pass Your Plumbing Exam` |
| `wordmark` | `["Pass Your ", "Plumbing", " Exam"]` (before / highlighted / after; only used when there is no logo image) |
| `tagline` | One line, shown in the footer and the social card |
| `fulfillment` | Leave as 1 Exam Prep unless a different store ships the orders |
| `phone`, `phoneTel`, `email` | The support contact for this brand |
| `logo` | `https://passyourplumbingexam.com/shared/logo.png` (made in step 3) |
| `logoNav` | `shared/logo-nav.png` (made in step 3) |
| `social` | The brand's social links, or empty strings |
| `repo` | `1ExamPrep/plumbing-exam` |
| `dashboardUrl` | `https://site-dashboard-c32v.onrender.com` |
| `siteKey` | Leave empty for now; the dashboard gives you one in step 7 |
| `launched` | Today's date, `YYYY-MM-DD` (used as datePublished in the schema) |

Leave `gtagId`, `gtmId`, `metaPixelId`, `ga4PropertyId`, `googleOAuthClientId`,
`googleSiteVerification` empty unless you have them.

---

## 3. Put the logo in

```bash
cp ~/Downloads/plumbing-logo.png brand/logo-source.png
python3 tools/make_logo.py
```

That writes `shared/logo-nav.png` (header), `shared/logo-mark.png` (square icon),
`shared/favicon.png`, `shared/apple-touch-icon.png` and `shared/logo.png` (1200×630
social card). The script splits the icon from the wordmark by looking for the gap
between them; if your logo has no separate icon, the mark will just be the whole logo,
which is fine.

No logo yet? Delete the `logoNav` line from `site-config.json` and the header shows
the text wordmark instead.

---

## 4. Point it at the products

The catalog (`shared/catalog.js` + `store/products-full.json`) is generated from the
Shopify collection. The dashboard does this for you once the site is connected
(step 7), but you can also pull it locally to test:

```bash
export SHOPIFY_STORE_DOMAIN=brown-1exam.myshopify.com
export SHOPIFY_ADMIN_TOKEN=shpat_...            # or use the dashboard instead
export SHOPIFY_COLLECTION_ID=123456789012
python3 tools/sync_shopify.py
```

**Important: the catalog rules are trade-specific.** `tools/build_catalog.py` (and its
twin in the dashboard, `server/shopify.js`) sort products into package tiers by
matching words in the Shopify titles:

- "ultimate combo" → Ultimate Combo
- "super combo" → Super Combo
- "calculations study guides & national electrical code combo" → Study Guide + Calculations + NEC
- "national electrical code combo with tabs" → Study Guide + NEC with Tabs
- "flash card combo" → Study Guide + Flash Cards
- singles: "online test success kit", "flash cards", "practical calculations", "exam prep and study guide"

They also detect the state from the title and the level (Journeyman / Master) and the
code year. If the new collection's titles follow the same pattern with different words
(say "plumbing code combo" instead of "national electrical code combo"), update the
`tier()` function in `tools/build_catalog.py` and `toCatalog()` in the dashboard's
`server/shopify.js` so the two agree, and update `INCLUDED` in `build.py` (the
"what's in the box" list per tier). If the products are not state + level + tier at
all, the listing pages need a different structure; that is a bigger change, ask before
starting.

Run the build and look at it:

```bash
pip install pillow
python3 build.py
python3 -m http.server 8000      # open http://localhost:8000
```

---

## 5. Change the copy that is trade-specific

The templates were written for electricians. Search for these and rewrite them for the
new trade (a plumbing exam does not reference the NEC):

- `store/template.html`: the hero headline, the "How it works" steps, the comparison
  table, the "How to choose the right package" guide, the FAQ block, the final CTA.
- `store/product.html`: the FAQ block and the assurance bullets under the Buy button.
- `build.py`: `LISTING_FAQ`, `PRODUCT_FAQ`, `BLOG_FAQ`, `INCLUDED`, the `takeaways`
  text in `listing_takeaways()` and the product page, the home-page title and lead, the
  `llms.txt` and `agents.md` text near the bottom.
- `content/faq-general.json`: the nationwide FAQ. Rewrite the answers for the trade;
  the structure (categories → items) stays.
- `store/blog-index.html`: the "Start here" and "What we write about" sections.
- `tools/blogkit.py` and the dashboard editor default the post author to the brand
  name, nothing to change.

The word "NEC" appears in a lot of places; `grep -rn "NEC" store build.py content`
finds them all.

---

## 6. Publish on GitHub Pages and the domain

1. Commit and push:
   ```bash
   git add -A && git commit -m "New site: Pass Your Plumbing Exam" && git push
   ```
2. GitHub → repo → **Settings → Pages** → Source: Deploy from a branch → `main`,
   `/ (root)` → Save. The site appears at `https://1examprep.github.io/plumbing-exam/`
   within a few minutes.
3. Custom domain: in the same Pages settings, enter `passyourplumbingexam.com` and
   Save (GitHub adds a `CNAME` file to the repo; pull it before your next push).
4. DNS at the registrar:
   - Four `A` records on the bare domain → `185.199.108.153`, `185.199.109.153`,
     `185.199.110.153`, `185.199.111.153`
   - `CNAME` for `www` → `1examprep.github.io`
5. Back in Pages settings, wait for "DNS check successful", then tick **Enforce HTTPS**
   (the box becomes clickable once the certificate is issued, usually within an hour,
   up to 24 h).
6. Make sure `siteUrl` in `site-config.json` is the real domain, rebuild, push. The
   canonical tags, sitemap, robots.txt, llms.txt and agents.md all key off it.

The two workflows in `.github/workflows/` are already in the copy:
- `build.yml` rebuilds the pages whenever the catalog, templates, config or content
  change, and when the dashboard asks it to. Nothing to configure.
- `sync-shopify.yml` is the old weekly sync. The dashboard replaces it; leave it
  without secrets and it will simply skip.

---

## 7. Connect it to the dashboard

Dashboard → **Connect a site**:

- Name: `Pass Your Plumbing Exam`
- Live URL: `https://passyourplumbingexam.com`
- GitHub repo: `1ExamPrep/plumbing-exam` + a fine-grained token with **Contents** and
  **Actions** read & write on that repo (GitHub → Settings → Developer settings →
  Fine-grained tokens). One token can cover several repos if you select them all.
- Shopify: domain `brown-1exam.myshopify.com` plus either the Admin API token or the
  Dev Dashboard app's Client ID and Client secret (the same ones the electrician site
  uses; the app is already installed on the store). Collection ID from step 0.

Save, then **Save and test connections** on the Settings page, pick the collection from
the dropdown, save again.

Now copy the two values from **Settings → Tracker** into `site-config.json`:

```json
"dashboardUrl": "https://site-dashboard-c32v.onrender.com",
"siteKey": "sk_xxxxxxxxxxxxxxxxxxxxxxxx"
```

Rebuild and push. From that moment every page view and Buy-now click shows up in the
dashboard.

Then **Sync & Deploy → Sync now**. The dashboard pulls the collection, commits the
catalog to the repo and triggers the build. Watch the bar; when it says Done, the
product pages are live a minute later.

---

## 8. Blog and Rankwork

The blog works from day one (empty index until there is a post). To let Rankwork
publish into it:

1. Dashboard → site → **Blog** → copy the hook URL from the Rankwork panel.
2. Rankwork → the new store's Integration page → Webhooks → **Add endpoint** with that
   URL → tick **Publish a page or blog post** → copy the `whsec_` signing secret.
3. Paste the secret into the Rankwork panel on the dashboard → Save secret.
4. Press **Test** in Rankwork; the test lands as a draft under Posts.

Posts can also be written in the dashboard editor, or pushed from any tool with the
generic webhook on the same page.

---

## 9. Check it

- https://passyourplumbingexam.com/ loads over HTTPS, header shows the logo.
- A state page lists the right packages and prices; a product page's Buy now opens
  checkout with the right item.
- `/faq/`, `/blog/`, `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/agents.md` all answer.
- Dashboard Overview shows visits after you click around the site.
- Run the site through Rankwork's audit (or Google's Rich Results Test on a product
  page) once; everything the electrician site passes, this one should too.

---

## Day-to-day

- **Products change in Shopify** → nothing to do. The dashboard syncs weekly (day and
  hour under Settings) and only commits when something changed. Sync now forces it.
- **Copy change** → edit the template or `build.py`, run `python3 build.py`, push.
  Or just push the source change; `build.yml` rebuilds on GitHub.
- **New post** → Rankwork, the dashboard editor, or a markdown file in `content/posts/`
  (see `tools/blogkit.py` for the front matter).
- **FAQ change** → `content/faq-general.json` for the nationwide set; state answers
  come from the Shopify descriptions, so fix those in Shopify.
- **Logo change** → replace `brand/logo-source.png`, run `python3 tools/make_logo.py`.

## Where things live

```
site-config.json        brand, domain, contact, dashboard hook
build.py                generates every page; copy and schema live here
store/*.html            page templates (listing, product, blog, FAQ, admin)
shared/                 CSS, JS, catalog.js, logo assets
content/posts/*.md      blog posts (front matter + Markdown or HTML)
content/faq-general.json nationwide FAQ
content/images/         hero images committed by the dashboard
content/redirects.json  old → new URLs when a post's handle changes
tools/                  sync_shopify.py, build_catalog.py, make_logo.py, blogkit.py
.github/workflows/      build.yml (rebuild on change / dispatch), sync-shopify.yml (legacy)
```

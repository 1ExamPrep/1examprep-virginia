# Pass Your Electrician Exam (electrician subsite)

**Making another site from this one?** Read [NEW-SITE.md](NEW-SITE.md).

## The live product page (start here)

`index.html` is the **1 Exam Prep product page**: the Scoreboard design (#3)
wired to your real Shopify catalog (the "2026 Electrician Exam Prep" collection,
522 products pulled from 1examprep.com on 2026-10-16).

### Every filter is in the URL

The site is generated as real folders, so every combination has its own address
that works when typed, shared, linked from an ad or indexed by Google:

```
/                                    home, state picker
/texas/journeyman/2026/              Texas · Journeyman · 2026 NEC (5 packages)
/texas/master/2026/                  Texas · Master
/texas/master/2026/ultimate-combo/   full product page: gallery, add-ons, description, related
/general/master/2026/                the non-state "general edition" packages
/new-york/journeyman/2026/           multi-word states use a dash
```

Package slugs: `study-guide-flash-cards`, `study-guide-nec-tabs`,
`study-guide-calculations-nec`, `super-combo`, `ultimate-combo`
(and `study-guide-nec` on the general edition).

Changing the state, level or year on the page updates the URL in place without a
reload, so the back button and copying the address bar both work. A `404.html`
catches near-misses like `/ohio/master/` or `/Texas/Journeyman/` and sends them
to the right page. Each generated page has its own `<title>`, meta description,
Open Graph tags and h1 for search.

The address never shows a file name: the page for `/texas/master/2026/` is stored
as `texas/master/2026/index.html`, and GitHub Pages serves it whenever that folder
is requested. Every link the site generates uses the clean form.

### Settings, search, phone and SEO

`site-config.json` holds the site-wide settings: brand, phone, email, social
links, logo, Google Search Console verification code, Google Analytics ID and,
most importantly, `siteUrl`. Edit it and run `python3 build.py`.

- **Search**: the magnifier in the header (or the `/` key) opens an instant
  search over states and all 522 products; `/search/?q=` is a full page used by
  the schema.org SearchAction. Runs in the browser, no server.
- **Phone**: `(877) 775-9400` in the header (tap-to-call on phones) and footer.
- **Footer**: contact, popular states, shop links, social links.
- **Schema.org** on every page: Organization + WebSite(SearchAction) + FAQPage on
  the home page; CollectionPage/ItemList + BreadcrumbList + FAQPage on state
  pages; Product (all variants as offers) + BreadcrumbList + FAQPage on product
  pages.
- **Head tags**: unique title and meta description, robots, canonical (when
  `siteUrl` is set), Open Graph, Twitter card, theme-color, favicon,
  apple-touch-icon, web manifest, optional Search Console and GA4 tags.
- **Structure**: one `h1` with `id="h1"` per page, sections with ids and
  `aria-labelledby`, skip link, `main`/`nav`/`footer` landmarks, alt text,
  lazy images.
- **Crawlers**: `robots.txt` (allows everything public, blocks the template
  designs and the search page, explicitly welcomes AI crawlers such as GPTBot,
  ClaudeBot and PerplexityBot), `llms.txt` (site summary for AI assistants
  with every state page linked), `sitemap.xml` with lastmod/priority when
  `siteUrl` is set.

### Automatic weekly update from Shopify

`.github/workflows/sync-shopify.yml` runs every Monday morning (and on demand
from the repo's Actions tab). It pulls the collection from Shopify with
`tools/sync_shopify.py`, rebuilds the catalog with `tools/build_catalog.py`, and
only if a title, price, description, image or variant changed does it rebuild
the site and push a commit. Unchanged weeks do nothing.

One-time setup (about five minutes):

1. In Shopify admin: Settings → Apps and sales channels → Develop apps → Create
   an app (name it "Site sync") → Configure Admin API scopes → tick
   `read_products` → Save → Install app → copy the **Admin API access token**
   (shown once).
2. In the GitHub repo: Settings → Secrets and variables → Actions → New
   repository secret, twice:
   - `SHOPIFY_STORE_DOMAIN` = your `something.myshopify.com` domain
   - `SHOPIFY_ADMIN_TOKEN` = the token from step 1
3. Actions tab → "Weekly Shopify sync" → Run workflow, to test it once.

The token only has read access to products; it cannot change anything in the
store. To sync a different collection set the `SHOPIFY_COLLECTION_ID` secret.

### Connecting to the site dashboard

Set `dashboardUrl` and `siteKey` in `site-config.json` (from the dashboard's
Settings → Tracker for this site), rebuild and push. Every page view and click
then goes to the dashboard as well as to Google Analytics, and the dashboard can
sync products into this repo (it commits `shared/catalog.js` and
`store/products-full.json`; `.github/workflows/build.yml` rebuilds the pages).

### Traffic and click tracking

`shared/track.js` runs on every page and sends events to Google Analytics 4
(and to Google Tag Manager / Meta Pixel if those IDs are set). Nothing loads
until `gtagId` is filled in. Events, with GA4 ecommerce fields where they exist:

| Event | When | Key fields |
|---|---|---|
| `view_item` | product page opened | item id/name, state, level, package, price |
| `select_item` | "What's inside" or a related-package card clicked | item, list location |
| `select_variant` | add-on option changed on a product page | item + variant |
| `begin_checkout` + `buy_now_click` | any Buy now button | item, variant, price, `button_location` (package_card, product_page, quick_view, sticky_bar, header, bottom_cta) |
| `search`, `search_open`, `search_result_click` | site search | search term |
| `filter_change` | state or level changed | state, level |
| `phone_click` | phone number tapped | location |
| `outbound_click` | link to 1examprep.com | url |
| `faq_open`, `package_swipe` | FAQ opened, phone swiper arrows | question / direction |

Register `button_location` as an event-scoped custom dimension in GA4 (Admin →
Custom definitions) to break Buy clicks down by button.

### Admin dashboard (`/admin/`)

Hidden from search engines. Shows, without any sign-in: catalog counts, price
range, duplicate listings found in Shopify, a filterable table of all products
with links to each page and the store, the last Shopify sync runs and the latest
site updates (from GitHub), and quick links (sitemap, robots, llms.txt, GA,
Search Console).

With Google sign-in it shows traffic and conversions for 7/28/90 days: sessions,
users, page views, Buy clicks and rate, checkout value clicked, phone taps,
searches; sessions and Buy clicks per day; Buy clicks by state, package, level
and button; all events; search terms; top pages; traffic sources; devices.
It reads GA4 directly in your browser with your own Google account (read-only),
so only people with access to the GA property can see the numbers.

Setup (one time, in `site-config.json`):
1. `gtagId`: GA4 measurement ID (G-…). Create a free GA4 property at
   analytics.google.com → Admin → Create property → Web data stream.
2. `ga4PropertyId`: the numeric property ID (Admin → Property details).
3. `googleOAuthClientId`: Google Cloud Console → APIs & Services → enable
   "Google Analytics Data API" → Credentials → Create OAuth client ID → Web
   application → Authorized JavaScript origins: your site's address (for now
   `https://1examprep.github.io`). Copy the client ID.
4. `python3 build.py` and push.

### Uploading only what changed

```bash
python3 make-update.py          # writes ../site-update.zip with just the changed and new files
python3 make-update.py --mark   # run after you upload, so the next update starts from here
```

The page's behaviour lives in `shared/store.js` and its styles in `shared/store.css`,
so a design or script fix is usually a one- or two-file upload. Only a change to
the page *markup* (`store/template.html`) or to the catalog regenerates all pages.

### Product pages

Every package URL is a full product page: six-image gallery, package name,
price with compare-at and savings, the add-on variants from Shopify (picking one
updates the price and the Buy link), a "What's in the package" list, the complete
Shopify description, related packages for the same state and level, and
schema.org Product data for Google. Buy now is the Shopify cart permalink.

### How to rebuild

```bash
python3 build.py                                   # regenerates index.html + all folders
python3 build.py --site https://prep.1examprep.com # same, plus sitemap.xml, robots.txt, canonical tags
python3 build.py --spa                             # optional lighter mode: 2 files, JS reads the URL (deep URLs return 404 status, not indexed)
```

Run it after any change to `store/template.html` (the page design) or
`shared/catalog.js` (the products). Old generated folders are cleaned up first,
using `generated-pages.txt`. Page CSS lives in `shared/store.css`.

- **Buy now** uses a Shopify cart permalink (`1examprep.com/cart/VARIANT:1`) so
  the item is added and the shopper lands on your checkout in one click.
- **What's inside** opens the description, the add-on variants (online course,
  flash cards, instructor videos) with live prices, and a link to the full
  product page on 1examprep.com.
- `shared/catalog.js` holds every product's image, title, description excerpt,
  price, compare-at price, year and variant IDs. Do not hand-edit it; when prices
  or products change, ask for a refresh and it is regenerated from Shopify, then
  run `build.py` again.
- The ten template designs are still in `designs/`, previewable from `gallery.html`.

Two catalog notes found while building it: Massachusetts Journeyman and
Minnesota Journeyman each have a duplicate "Study Guide + NEC with Tabs" listing
(handle ends in `-1`, $249.95) where the "+ Calculations" package ($279.95) is
for every other state, and the Pennsylvania Journeyman Ultimate Combo "+ Videos" variant
shows a compare-at price ($495) lower than its price ($499.95). The page hides
the duplicates; the compare-at is shown as Shopify has it.

---

# Template landing pages (designs 1–10)

Ten ready-to-host landing pages for selling master electrician exam prep packs.
Every page reads the same product list, so you edit prices, descriptions and
checkout links in **one file** and all five update.

```
electrician-site/
├── index.html            ← LIVE product page (generated by build.py)
├── <state>/<level>/<year>/[package]/index.html   ← 612 generated pages, one per URL
├── build.py              ← generates all of the above from the template + catalog
├── 404.html              ← sends near-miss URLs to the right page
├── gallery.html          ← preview of the 10 template designs
├── store/template.html   ← the state listing page design (edit, then run build.py)
├── store/product.html    ← the product page design
├── store/products-full.json ← full descriptions + 6 images per product (from Shopify, build-time only)
├── shared/product.js     ← product page behaviour (variant price, gallery)
├── shared/store.css      ← product page styles
├── shared/store.js       ← product page behaviour (picker, routing, modal)
├── make-update.py        ← zips only files changed since your last upload
├── shared/catalog.js     ← 522 products pulled from Shopify (auto-generated)
├── designs/
│   ├── 1-livewire.html
│   ├── 2-blueprint.html
│   ├── 3-scoreboard.html
│   ├── 4-readiness.html
│   ├── 5-cobalt.html
│   ├── 6-kinetic.html      ← designs 6–10 use GSAP (loaded from a CDN) for scroll motion
│   ├── 7-storyboard.html
│   ├── 8-depth.html
│   ├── 9-signal.html
│   └── 10-glass.html
├── shared/
│   ├── products.js       ← EDIT THIS: names, prices, descriptions, checkout links
│   ├── app.js            ← renders products, detail popups, buy buttons (no edits needed)
│   └── base.css          ← shared structure (no edits needed)
├── make-homepage.sh      ← one command to turn a design into index.html
├── .nojekyll
└── CNAME.example         ← rename to CNAME when you connect your own domain
```

## 1. Add your checkout links

Open `shared/products.js`. Each product looks like this:

```js
{
  id: "master-520",
  name: "Master Study Pack",
  short: "520 questions + readiness tracker",
  price: "$74.95",
  compareAt: "",              // optional "was" price, e.g. "$89.95"
  badge: "Most popular",      // optional ribbon; "Most popular" also powers the hero Buy button
  access: "90-day access",
  description: "Long description shown in the 'What's inside' popup...",
  features: ["Bullet one", "Bullet two"],
  checkout: "PASTE_CHECKOUT_LINK_HERE"   // ← your Stripe / Shopify / PayPal / Gumroad link
}
```

Replace every `PASTE_CHECKOUT_LINK_HERE` with the real URL. Until you do, the
Buy buttons show a small reminder instead of going anywhere.

Add a product by copying a whole `{ ... }` block. Remove one by deleting it.
At the top of the same file, `SITE.brand`, `SITE.supportEmail` and
`SITE.states` fill in the brand name, support email and the states list.

How buying works on every page: **Buy now** goes straight to your checkout URL.
**What's inside** opens a popup with the full description and a bigger
Buy now button that also goes straight to checkout.

## 2. Pick a design and make it the homepage

Preview all ten by opening `gallery.html` in a browser (or on GitHub Pages after step 3).

Then either run:

```bash
./make-homepage.sh 3        # 1–10, the design number
```

or do it by hand: copy the design file over `index.html` and change the two
`../shared/` paths inside it to `shared/`.

Compare the designs on the gallery page; one line on each:

| # | Name | Feel | Signature motion |
|---|------|------|------------------|
| 1 | Live Wire | Dark navy + hazard yellow | Current pulses running through a circuit panel |
| 2 | Blueprint | Drafting paper + cobalt ink | One-line diagram draws itself on load |
| 3 | Scoreboard | Off-white + hot orange | Headline animates word by word, spinning gauge, marquee |
| 4 | Readiness | White + forest green, serif | Live readiness-score widget cycling through sittings |
| 5 | Cobalt | Cobalt blue + lime | Interactive sample question, cursor glow, 3D tilt cards |
| 6 | Kinetic | Cool grey + violet | Giant drifting type, pinned horizontal product rail, line reveals |
| 7 | Storyboard | Plum mesh gradient + peach | Custom cursor, magnetic buttons, pinned 3-card story |
| 8 | Depth | Pale blue + tangerine | Parallax floating cards, mouse depth, scroll-scrubbed exam clock |
| 9 | Signal | White + black + signal red | Decoding headline, giant outlined scroll type, expandable list |
| 10 | Glass | Lavender/aqua mesh | Frosted bento hero, sample question, 3D cover-flow packs |

Designs 6–10 load GSAP 3.13 from cdnjs for the scroll-driven motion. They degrade
cleanly: if the CDN is blocked, the pages still render and every Buy button works,
you just lose the fancy motion. All ten respect "reduce motion" settings.

## 3. Put it on GitHub Pages

1. Create a new repository on GitHub (e.g. `masterprep-site`).
2. Upload everything in this folder (drag and drop on github.com works, or `git push`).
3. In the repo go to **Settings → Pages**. Under *Build and deployment* choose
   **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
4. After a minute your site is live at `https://YOUR-USERNAME.github.io/masterprep-site/`.

`.nojekyll` is included so GitHub serves the files exactly as they are.

## 4. Connect your own domain

1. Rename `CNAME.example` to `CNAME` and put your domain inside it on one line,
   e.g. `www.yourdomain.com`. Commit and push.
2. At your domain registrar add DNS records:
   - For `www`: a **CNAME** record pointing to `YOUR-USERNAME.github.io`
   - For the bare domain (`yourdomain.com`): four **A** records to
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
3. Back in **Settings → Pages**, enter the domain under *Custom domain* and tick
   **Enforce HTTPS** once the certificate appears (can take up to an hour).

## Optional tweaks

- **Hero button product**: the hero and sticky-bar Buy buttons point at the product
  whose `badge` contains "popular". Change the badge to move it.
- **Colours and fonts**: each design's colours are the `:root` variables at the top
  of its HTML file.
- **Topic percentages** in the "What's covered" sections are plain text in each
  design file; edit them to match your bank.
- **FAQ**: plain `<details>` blocks in each file. Add your refund policy there.
- **Analytics**: paste your tag snippet before `</head>` in the design you use.

## Honesty notes baked in

The pages say the questions are original practice material, not the real exam,
and that buying does not grant eligibility or a license. Keep those lines; they
protect you and they match what the research report found about these products.


## Blog

Posts are Markdown files in `content/posts/<slug>.md` with a small front matter block
(title, date, author, excerpt, image, tags, state, level, status). `build.py` renders
`/blog/`, one page per post, `/blog/tag/<tag>/`, `/blog/feed.xml` (RSS) and
`/blog/posts.json`, and adds them to the sitemap and `llms.txt`. Posts with
`status: draft` are skipped.

Write them by hand and push, or let the dashboard do it: its Blog page has an editor
and a webhook (`POST /hooks/blog/<site key>`) that commits the file here and triggers
`build.yml`. A post can carry `state: Texas` and `level: Master` so its call-to-action
points at that state's packages.


## Brand and fulfillment

The site speaks as its own brand. `site-config.json` holds `brand` (name), `wordmark`
(three parts for the header logo: before, accent, after), `tagline`, and `fulfillment`
(`name`, `url`, `note`): the store that processes and ships orders. Every template uses
`{{BRAND}}`, `{{WORDMARK}}`, `{{FULFILL_NAME}}`; the JS reads `window.SITE`. `build.py`
uses the logo assets in `shared/` (made by `tools/make_logo.py` from
`brand/logo-source.png`: header logo, square mark, favicon, apple-touch icon, 1200x630
social card); without them it falls back to a text wordmark and generated icons. Store descriptions that mention the fulfillment
brand are rewritten to the site's brand at build time. To spin up another subsite:
copy the repo, change `brand`, `wordmark`, `tagline`, `siteUrl`, `repo`, `siteKey`, and
point the dashboard at a different Shopify collection.


## FAQ

`/faq/` is the nationwide FAQ (edit `content/faq-general.json`), and `/faq/<state>/<level>/`
holds the state-specific questions, which `build.py` extracts from the FAQ block inside each
Shopify product description, de-duplicates per state and level, and groups into The exam /
Licensing and experience / Code book and materials. Every FAQ page carries FAQPage schema,
a Key takeaways box, a client-side filter box and links to the matching packages. Counts
update automatically when products or descriptions change.

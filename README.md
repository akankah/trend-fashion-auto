# Trend Fashion Auto

SEO-optimized website otomatis yang mengambil data fashion wanita dari Collshp (Shopee affiliate) via GraphQL API, generate halaman HTML statis, dan deploy ke Cloudflare Pages tiap 2 jam.

**Live:** https://trend-fashion-auto.pages.dev

## Fitur

- **Crawler API-first**: Collshp GraphQL API (`/api/v3/gql/graphql`) ambil semua produk (totalCount ~1100+), Playwright hanya untuk resolve shortlink redirect. Retry 1x dengan delay 10s untuk timeout/connection error
- **Auto-filter wanita**: Hanya produk fashion wanita (65+ keyword non-women difilter otomatis)
- **Auto-remove**: Produk yang sudah tidak ada di Collshp otomatis dihapus tiap crawl (filter by shortlink)
- **Dedup by shortlink**: Produk sama dengan shortlink berbeda tetap muncul (duplicate affiliate links diperbolehkan). Slug dedup counter-based (`-2`, `-3`) untuk judul duplikat
- **Home-highlights scroll horizontal**: 15 produk terbaru + 15 produk terlaris (30 total) dengan horizontal scroll. Desktop: arrow buttons ❮❯. Mobile: touch scroll. Teknik CSS: outer `overflow-x:auto` + inner `flex;min-width:max-content` + grid item `min-width:0` fix
- **Floating category bar**: Sticky horizontal scroll kategori (`position:sticky;top:56px;z-index:99`) — muncul di index, kategori, halaman produk
- **Infinite scroll**: 24 produk awal rendered, sisanya load dari `products_display.json` via IntersectionObserver
- **Auto-generated articles**: 7+ artikel roundup + rekomendasi per-kategori dari produk real
- **6 kategori**: Outer, Dress, Tunik, Atasan, Bawahan, Hijab
- **JSON-LD schema**: Organization, Product (tanpa harga - cek di Shopee), Article, FAQPage, WebPage
- **E-E-A-T**: About page dengan author bio, "5 tahun pengalaman fashion digital"
- **Harga**: Format `Rp65.000` (Indonesia, pakai titik)
- **Product description**: Dinamis dari kombinasi MATERIALS, STYLES, SIZES variatif (10 template)
- **Share buttons**: FB, WA, Telegram, LINE, Email, Copy Link
- **Facebook page link**: Footer semua halaman + About page
- **Mobile responsive**: Footer 2 baris seragam `#ccc`, layout responsif semua halaman
- **Static pages**: About, Contact, FAQ, Privacy Policy, Disclaimer, Affiliate Disclosure

## Teknologi

- **Crawler**: Python + requests (GraphQL) + Playwright (shortlink resolve)
- **Generator**: Python + Jinja2 → HTML statis
- **Hosting**: Cloudflare Pages (free)
- **CI/CD**: GitHub Actions (cron `0 */2 * * *` + push + manual dispatch)

## Arsitektur Scroll Horizontal

```
.hl-scroll-wrap { position:relative }
  button.hl-scroll-left ❮
  .products.hl-scroll { display:block; overflow-x:auto }
    .hl-scroll-inner { display:flex; min-width:max-content }
      .product-card { flex-shrink:0; width:220px (desktop) / 170px (mobile) }
  button.hl-scroll-right ❯
```

**Key fix:** `.hl-col{min-width:0}` — CSS Grid item default `min-width:auto` mencegah overflow scrolling pada child. `min-width:0` pada grid item memungkinkan `overflow-x:auto` berfungsi.

## Status

- ✅ GraphQL API crawler (bukan Playwright DOM scrape)
- ✅ 1036+ produk fashion wanita live
- ✅ Harga format Rp tanpa spasi (Rp65.000)
- ✅ Home-highlights scroll horizontal (desktop arrows + mobile touch)
- ✅ Floating category bar sticky + horizontal scroll
- ✅ Infinite scroll + IntersectionObserver lazy load
- ✅ Artikel auto-generated dari produk real
- ✅ JSON-LD structured data (Product, Article, FAQ, Organization, WebPage)
- ✅ E-E-A-T About page + Facebook page
- ✅ Mobile responsive (footer 2 baris, cat-float scroll)
- ✅ Auto-update tiap 2 jam via GitHub Actions
- ✅ Auto-commit data/products.json dengan `[skip ci]` (no infinite loop)

## Setup Lokal

```bash
pip install -r requirements.txt
python -m playwright install chromium
set COLLSHP_SOURCE=https://collshp.com/shopeemurahkekinian
python crawler_playwright.py
python generate_site.py
npx wrangler pages deploy generated --project-name=trend-fashion-auto
```

## Env

| Variable | Default | Keterangan |
|---|---|---|
| `SITE_NAME` | Trend Fashion Auto | Nama situs |
| `SITE_URL` | https://trend-fashion-auto.pages.dev | Base URL |
| `COLLSHP_SOURCE` | https://collshp.com/shopeemurahkekinian | Sumber data Collshp |
| `CLOUDFLARE_API_TOKEN` | - | Token deploy (via env/secrets) |

## Troubleshooting CSS Grid Scroll

**Problem:** Child dengan `overflow-x:auto` tidak bisa scroll di dalam CSS Grid item.

**Fix:** Tambah `min-width:0` pada grid item (`.hl-col`). Default `min-width:auto` pada grid item mencegah overflow scrolling karena grid item tidak bisa mengecil di bawah kontennya.

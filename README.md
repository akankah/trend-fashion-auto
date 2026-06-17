# Trend Fashion Auto

SEO-optimized website otomatis yang mengambil data fashion wanita dari Collshp (Shopee affiliate) via GraphQL API, generate halaman HTML statis, dan deploy ke Cloudflare Pages tiap 2 jam.

**Live:** https://trend-fashion-auto.pages.dev

## Fitur

- **Crawler API-first**: Collshp GraphQL API (`/api/v3/gql/graphql`) ambil semua produk (totalCount ~1100+), Playwright hanya untuk resolve shortlink redirect
- **Auto-filter**: Hanya produk wanita (65+ keyword non-women diffilter otomatis). Filter diperbarui tiap crawl
- **Auto-remove**: Produk yang sudah tidak ada di Collshp otomatis dihapus dari situs tiap crawl
- **Infinite scroll**: 24 produk awal, 24 lagi tiap scroll (IntersectionObserver)
- **Floating category bar**: Sticky horizontal scroll kategori di index, kategori, produk
- **Auto-generated articles**: Artikel roundup + rekomendasi per-kategori dari produk real
- **JSON-LD schema**: Organization, Product (harga + rating + offer), Article, FAQPage, WebPage
- **E-E-A-T**: About page dengan author bio, "5 tahun pengalaman fashion digital"
- **Harga format IDR**: Rp65.000 (thousand separator titik)
- **2 user reviews per produk**: Auto-generated dari template variatif
- **Produk description**: Dinamis dari kombinasi MATERIALS, STYLES, SIZES
- **Share buttons**: FB, WA, Telegram, LINE, Email, Copy Link
- **Facebook page link**: Footer semua halaman + About page
- **Mobile responsive**: Footer 2 baris (© + Artikel + Tentang + FAQ | Kontak + Privasi + Disclaimer + Afiliasi + Facebook)
- **6 kategori**: Outer, Dress, Tunik, Atasan, Bawahan, Hijab

## Teknologi

- **Crawler**: Python + requests (GraphQL) + Playwright (shortlink resolve)
- **Generator**: Python + Jinja2 → HTML statis
- **Hosting**: Cloudflare Pages (free)
- **CI/CD**: GitHub Actions (cron `0 */2 * * *` + push + manual dispatch)

## Cara Kerja

1. **Crawl**: Request `getLinkLists` GraphQL → dapat semua shortlink + metadata. Filter link `s.shopee.co.id`. Playwright resolve redirect ke URL Shopee asli. Dedup by `(shopid, itemid)`. Hapus produk yang sudah tidak ada di Collshp.
2. **Generate**: Jinja2 render 797+ product pages, index (infinite scroll), 6 kategori, 7+ artikel auto-generated, 6 halaman statis (about, faq, contact, privacy, disclaimer, affiliate-disclosure), sitemap.xml
3. **Deploy**: wrangler deploy ke Cloudflare Pages `trend-fashion-auto`

## Link Afiliasi

Semua tombol "Lihat Produk di Shopee" pakai shortlink Collshp (`s.shopee.co.id/xxx`) — komisi affiliate tetap jalan. Prioritas: `shortlink` → `url` → direct Shopee link.

## Status

- ✅ GraphQL API crawler (bukan Playwright DOM scrape)
- ✅ 800+ produk fashion wanita live
- ✅ Harga format Rp tanpa spasi (Rp65.000)
- ✅ Infinite scroll + floating kategori
- ✅ Artikel auto-generated dari produk real
- ✅ JSON-LD structured data (Product, Article, FAQ, Organization)
- ✅ E-E-A-T About page + Facebook page
- ✅ Mobile responsive (footer 2 baris, cat-float horizontal scroll)
- ✅ Auto-update tiap 2 jam via GitHub Actions

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

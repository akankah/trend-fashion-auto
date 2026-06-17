# Trend Fashion Auto

SEO-optimized website otomatis yang mengambil data dari Collshp (Shopee affiliate), generate halaman HTML statis, dan deploy ke Cloudflare Pages.

## Teknologi

- **Crawler**: Playwright (headless Chromium) untuk scrape Collshp yang JS-heavy
- **Generator**: Python + Jinja2 → halaman HTML statis
- **Hosting**: Cloudflare Pages
- **CI/CD**: GitHub Actions (update otomatis tiap 2 jam)

## Cara Kerja

1. Playwright buka Collshp → ambil shortlink `s.shopee.co.id/xxx` + gambar produk
2. Simpan ke `data/products.json`
3. Jinja2 generate: index, kategori, halaman produk, sitemap, halaman statis
4. Deploy ke Cloudflare Pages via wrangler CLI
5. GitHub Actions cron `0 */2 * * *` jalanin semua otomatis

## Link Afiliasi

Semua tombol "Lihat Produk di Shopee" menggunakan shortlink Collshp (`s.shopee.co.id/xxx`) — komisi affiliate tetap jalan.

## Status

✅ Crawler Playwright ambil produk real dari Collshp
✅ Gambar dari Shopee CDN
✅ Design ala Shopee (orange, card, star rating, price)
✅ Mobile responsive (produk di atas, kategori di bawah)
✅ SEO (meta tags, canonical, sitemap.xml)
✅ Deploy otomatis tiap 2 jam via GitHub Actions
✅ Live: https://trend-fashion-auto.pages.dev

## Setup Lokal

```bash
pip install -r requirements.txt
python -m playwright install chromium
python crawler_playwright.py
python generate_site.py
npx wrangler pages deploy generated --project-name trend-fashion-auto
```

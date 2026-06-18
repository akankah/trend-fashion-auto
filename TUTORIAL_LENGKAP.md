# TUTORIAL LENGKAP: Auto SEO Website dari Collshp

## 📌 Tujuan
Bikin website SEO otomatis dari Collshp → Crawl produk via GraphQL API → Generate HTML statis → Hosting gratis Cloudflare Pages → Update tiap 2 jam via GitHub Actions.

## 📁 Struktur Final Project

```
E:\cuanseo/                      ← folder kerja lokal
├── .github/workflows/update.yml ← GitHub Actions (auto deploy + auto-commit data)
├── generated/                   ← output HTML (auto-generated, di-ignore git)
│   ├── index.html
│   ├── sitemap.xml
│   ├── style.css
│   ├── p/                       ← 1036+ halaman produk
│   ├── kategori/                ← 6 halaman kategori
│   ├── artikel/                 ← 7+ artikel auto-generated
│   ├── data/products_display.json
│   ├── about.html, contact.html, privacy-policy.html, ...
├── data/products.json           ← database produk (hasil crawl)
├── templates/                   ← Jinja2 HTML templates
│   ├── index.html
│   ├── product.html
│   ├── category.html
│   ├── article.html
│   ├── page.html
├── static/style.css             ← stylesheet
├── crawler_playwright.py        ← GraphQL API crawler
├── generate_site.py             ← generator HTML SEO
├── wrangler.toml                ← config Cloudflare Pages deploy
├── .env                         ← config environment
├── .gitignore
├── requirements.txt
├── TUTORIAL_LENGKAP.md          ← file ini
```

---

## 🪜 Langkah-langkah Detail

### 1. Buat Struktur Folder
```
mkdir .github/workflows generated data
```

### 2. File `.env`
```
COLLSHP_SOURCE=https://collshp.com/shopeemurahkekinian?share_channel_code=2
SITE_NAME=Trend Fashion Auto
SITE_URL=https://trend-fashion-auto.pages.dev
UPDATE_INTERVAL=120
```

### 3. File `requirements.txt`
```
requests
jinja2
```

### 4. File `crawler_playwright.py`
Crawler via Collshp GraphQL API:
- Request `getLinkLists` GraphQL → dapat semua shortlink + metadata
- Filter link `s.shopee.co.id`
- Playwright resolve redirect → URL asli Shopee
- Extract `shopid` & `itemid` & `image`
- Dedup by shortlink (bukan shopid/itemid — agar produk sama dengan shortlink affiliate beda tetap muncul)
- Auto-remove produk yang tidak ada di Collshp
- Filter non-women products (65+ keywords)
- Retry 1x dengan 10s delay untuk timeout/connection error

### 5. File `generate_site.py`
Generator SEO dengan Jinja2:
- Baca `data/products.json`
- Klasifikasi produk ke 6 kategori (outer, dress, tunik, atasan, bawahan, hijab)
- Sort by `date_added` descending (terbaru di atas)
- Home-highlights: 15 produk terbaru + 15 produk terlaris dengan horizontal scroll
- Counter-based slug dedup untuk judul duplikat (`-2`, `-3`)
- Generate 1036+ product pages, index (infinite scroll), 6 kategori, 7+ artikel, 6 halaman statis, sitemap.xml
- JSON-LD: Organization, Product, Article, FAQPage, WebPage

### 6. CSS Scroll Horizontal (Key Technique)
```
.hl-scroll-wrap { position:relative }
  button.hl-scroll-left ❮
  .products.hl-scroll { display:block; overflow-x:auto }
    .hl-scroll-inner { display:flex; min-width:max-content }
      .product-card { flex-shrink:0; width:220px(D)/170px(M) }
  button.hl-scroll-right ❯
```

**Critical fix:** `.hl-col{min-width:0}` — CSS Grid item default `min-width:auto` blocks overflow scrolling. Adding `min-width:0` on the grid item allows `overflow-x:auto` to work.

### 7. File `wrangler.toml`
```toml
name = "trend-fashion-auto"
pages_build_output_dir = "generated"
```

### 8. File `.github/workflows/update.yml`
GitHub Actions workflow:
```yaml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 */2 * * *'       # tiap 2 jam
  workflow_dispatch:              # trigger manual

steps:
  - git checkout
  - setup Python
  - pip install -r requirements.txt
  - python crawler_playwright.py # crawl via GraphQL API
  - python generate_site.py      # generate HTML
  - commit data/products.json dengan [skip ci]
  - npx wrangler pages deploy    # deploy ke Cloudflare
```

### 9. Git Init & Push ke GitHub
```bash
git init
git add -A
git commit -m "Initial setup"
git branch -m main
git remote add origin https://github.com/akankah/trend-fashion-auto.git
git push -u origin main
```

### 10. Cloudflare API Token
Buat token di [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens):
- **Create Custom Token**
- Permission: **Cloudflare Pages → Edit**
- Account: pilih akunmu

### 11. GitHub Secrets
Buka [github.com/akankah/trend-fashion-auto/settings/secrets/actions](https://github.com/akankah/trend-fashion-auto/settings/secrets/actions)
- **New repository secret**
- **Name:** `CF_API_TOKEN`
- **Value:** paste token Cloudflare

### 12. Test Deploy
Trigger workflow dari GitHub Actions → **Run workflow**

Atau push commit → auto trigger:
```bash
git commit --allow-empty -m "trigger deploy"
git push
```

---

## 🌐 Hasil Akhir
| URL | Keterangan |
|---|---|
| https://trend-fashion-auto.pages.dev | Website live (1036+ produk) |
| https://trend-fashion-auto.pages.dev/sitemap.xml | Sitemap |
| https://github.com/akankah/trend-fashion-auto | GitHub repo |

---

## 🔄 Cara Kerja

```
Collshp.com
    ↓ (GitHub Actions tiap 2 jam)
crawler_playwright.py → GraphQL API → semua produk
    ↓ Playwright resolve shortlink redirect
data/products.json (dedup by shortlink, auto-remove stale)
    ↓
generate_site.py → 1036+ HTML SEO pages
    ↓
wrangler pages deploy → Cloudflare Pages
    ↓
Website update otomatis
```

## ⚙️ Fitur Lengkap
- Home-highlights: 15 produk terbaru + 15 terlaris (horizontal scroll, desktop arrows ❮❯, mobile touch)
- Floating category bar (sticky, horizontal scroll)
- Infinite scroll (IntersectionObserver, batch 24)
- Auto-generated articles (7+ dari produk real)
- JSON-LD structured data + E-E-A-T pages
- Share buttons (FB, WA, Telegram, LINE, Email, Copy Link)
- Mobile responsive (footer 2 baris, cat-float scroll)
- Auto-update tiap 2 jam + auto-commit data dengan `[skip ci]`

## 🚨 Troubleshooting

| Error | Solusi |
|---|---|
| `Missing account_id` | Tambah `CLOUDFLARE_ACCOUNT_ID` di env workflow |
| `401 Unauthorized` (token) | Buat ulang Cloudflare API token |
| Scroll horizontal tidak work | Pastikan `.hl-col{min-width:0}` ada — ini fix CSS Grid `min-width:auto` |
| Workflow gak trigger | Tambah `push` trigger di workflow yml |
| No Pages project | Deploy via wrangler akan auto-create project |

---

**Selesai.** 🎉

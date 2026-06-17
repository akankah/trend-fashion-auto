# TUTORIAL LENGKAP: Auto SEO Website dari Collshp

## 📌 Tujuan
Bikin website SEO otomatis dari Collshp → Crawl produk → Generate HTML → Hosting gratis Cloudflare Pages → Update tiap 2 jam via GitHub Actions.

## 📁 Struktur Final Project

```
E:\cuanseo/                      ← folder kerja lokal
├── .github/workflows/update.yml ← GitHub Actions (auto deploy)
├── generated/                   ← output HTML (auto-generated, di-ignore git)
│   ├── index.html
│   ├── sitemap.xml
│   ├── p/                       ← halaman produk (SEO + FAQ)
│   ├── kategori/                ← halaman kategori
│   ├── about.html, contact.html, privacy-policy.html, ...
├── data/products.json           ← database produk (hasil crawl)
├── templates/                   ← Jinja2 HTML templates
│   ├── index.html
│   ├── product.html
│   ├── category.html
│   ├── page.html
├── crawler.py                   ← scraper Collshp → extract Shopee IDs
├── generate_site.py             ← generator HTML SEO dari data produk
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
beautifulsoup4
jinja2
```

### 4. File `.gitignore`
```
__pycache__/
*.pyc
.env
generated/
```

### 5. File `crawler.py`
Crawler scraping Collshp:
- Ambil halaman Collshp
- Cari semua link `s.shopee.co.id`
- Follow redirect → dapat URL asli Shopee
- Extract `shopid` & `itemid`
- Simpan ke `data/products.json` (dedup)

### 6. File `generate_site.py`
Generator SEO:
- Baca `data/products.json`
- Klasifikasi produk ke kategori (outer, dress, tunik, dll)
- Generate FAQ otomatis per produk
- Generate halaman: index, produk, kategori, statis (about, contact, privacy, disclaimer, affiliate-disclosure)
- Generate `sitemap.xml`

### 7. Templates (`templates/`)
- `product.html` — SEO product page + FAQ schema
- `category.html` — category listing
- `index.html` — homepage + recent products
- `page.html` — static pages template

### 8. File `wrangler.toml`
```toml
name = "trend-fashion-auto"
pages_build_output_dir = "generated"
```

### 9. File `.github/workflows/update.yml`
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
  - python crawler.py            # crawl Collshp
  - python generate_site.py      # generate HTML
  - npx wrangler pages deploy    # deploy ke Cloudflare
```

### 10. Git Init & Push ke GitHub
```bash
git init
git add -A
git commit -m "Initial setup"
git branch -m main
git remote add origin https://github.com/akankah/trend-fashion-auto.git
git push -u origin main
```

### 11. Cloudflare API Token
Buat token di [dash.cloudflare.com/profile/api-tokens](https://dash.cloudflare.com/profile/api-tokens):
- **Create Custom Token**
- Permission: **Cloudflare Pages → Edit**
- Account: pilih akunmu

### 12. GitHub Secrets
Buka [github.com/akankah/trend-fashion-auto/settings/secrets/actions](https://github.com/akankah/trend-fashion-auto/settings/secrets/actions)
- **New repository secret**
- **Name:** `CF_API_TOKEN`
- **Value:** paste token Cloudflare

### 13. Test Deploy
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
| https://trend-fashion-auto.pages.dev | Website live |
| https://trend-fashion-auto.pages.dev/sitemap.xml | Sitemap |
| https://trend-fashion-auto.pages.dev/p/metta-outer-organza-wanita.html | Contoh produk |
| https://github.com/akankah/trend-fashion-auto | GitHub repo |

---

## 🔄 Cara Kerja

```
Collshp.com
    ↓ (GitHub Actions tiap 2 jam)
crawler.py → ambil link Shopee
    ↓
data/products.json
    ↓
generate_site.py → HTML SEO
    ↓
wrangler pages deploy → Cloudflare Pages
    ↓
Website update otomatis
```

## ⚙️ Pengembangan Lanjutan
- Ganti `SITE_URL` di `.env` kalau pakai custom domain
- Tambah CSS biar tampilannya lebih proper
- Integrasi Google Indexing API biar cepet terindex
- Tambah RSS Feed
- Tambah Telegram Auto Post

## 🚨 Troubleshooting

| Error | Solusi |
|---|---|
| `Missing account_id` | Tambah `CLOUDFLARE_ACCOUNT_ID` di env workflow |
| `401 Unauthorized` (token) | Buat ulang Cloudflare API token |
| Workflow gak trigger | Tambah `push` trigger di workflow yml |
| No Pages project | Deploy via wrangler akan auto-create project |
| Token expired | Buat baru di dashboard Cloudflare |

---

**Selesai.** 🎉

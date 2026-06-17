import os
import json
import re
import shutil
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

DATA_FILE = "data/products.json"
OUTPUT_DIR = "generated"
TEMPLATE_DIR = "templates"
SITE_NAME = os.getenv("SITE_NAME", "Trend Fashion Auto")
SITE_URL = os.getenv("SITE_URL", "https://trend-fashion-auto.pages.dev")
PLACEHOLDER_IMAGE = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' fill='%23f0f0f0'%3E%3Crect width='400' height='400'/%3E%3Ctext x='200' y='200' text-anchor='middle' fill='%23999' font-size='16'%3EProduct%3C/text%3E%3C/svg%3E"

CATEGORIES = [
    {"name": "Outer", "slug": "outer", "keywords": ["outer", "jaket", "cardigan", "blazer"]},
    {"name": "Dress", "slug": "dress", "keywords": ["dress", "gaun", "rok"]},
    {"name": "Tunik", "slug": "tunik", "keywords": ["tunik", "baju muslim", "gamis"]},
    {"name": "Atasan", "slug": "atasan", "keywords": ["atasan", "blouse", "kemeja"]},
    {"name": "Bawahan", "slug": "bawahan", "keywords": ["celana", "rok", "legging"]},
    {"name": "Hijab", "slug": "hijab", "keywords": ["hijab", "jilbab", "khimar"]},
]

TAGS = [
    {"name": "Muslimah", "slug": "muslimah"},
    {"name": "Kondangan", "slug": "kondangan"},
    {"name": "Formal", "slug": "formal"},
    {"name": "Casual", "slug": "casual"},
    {"name": "Daily Wear", "slug": "daily-wear"},
]

STATIC_PAGES = {
    "about": {"title": "Tentang Kami", "content": "<p>Kami adalah platform yang menyediakan informasi produk fashion terbaru dan terpopuler dari berbagai toko online terpercaya.</p>"},
    "contact": {"title": "Kontak Kami", "content": "<p>Hubungi kami melalui email: contact@example.com</p>"},
    "privacy-policy": {"title": "Kebijakan Privasi", "content": "<p>Kami menghargai privasi Anda. Data pengguna tidak akan dijual atau disebarkan ke pihak ketiga.</p>"},
    "disclaimer": {"title": "Disclaimer", "content": "<p>Konten di situs ini bersifat informatif. harga dan ketersediaan produk dapat berubah sewaktu-waktu.</p>"},
    "affiliate-disclosure": {"title": "Pengungkapan Afiliasi", "content": "<p>Situs ini menggunakan link afiliasi. Kami dapat memperoleh komisi dari pembelian yang dilakukan melalui link ini.</p>"},
}

def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def classify_product(title):
    title_lower = title.lower()
    for cat in CATEGORIES:
        if any(kw in title_lower for kw in cat["keywords"]):
            return cat
    return CATEGORIES[0]

def generate_faqs(title, category_name):
    return [
        {"q": f"Apa itu {title}?", "a": f"{title} adalah produk fashion kategori {category_name} yang sedang populer dan banyak dicari."},
        {"q": f"Berapa harga {title}?", "a": f"Harga {title} bervariasi tergantung toko dan promo yang sedang berlangsung. Cek link di bawah untuk info harga terbaru."},
        {"q": f"Dimana bisa beli {title}?", "a": f"Kamu bisa membeli {title} melalui link afiliasi yang tersedia di halaman ini."},
        {"q": f"Apakah {title} tersedia dalam berbagai ukuran?", "a": f"Ketersediaan ukuran {title} tergantung pada masing-masing toko. Silakan cek deskripsi produk di halaman Shopee."},
    ]

def generate_product_page(env, product):
    title = product.get("title") or f"Produk Shopee {product['shopid']}.{product['itemid']}"
    cat = classify_product(title)
    slug = slugify(title) or f"produk-{product['shopid']}-{product['itemid']}"
    description = f"Beli {title} dengan harga terbaik. Produk fashion kategori {cat['name']} terbaru dan terlaris."
    affiliate_url = product.get("url") or f"https://shopee.co.id/product/{product['shopid']}/{product['itemid']}"

    template = env.get_template("product.html")
    html = template.render(
        title=title,
        slug=slug,
        site_name=SITE_NAME,
        site_url=SITE_URL,
        description=description,
        image=product.get("image") or PLACEHOLDER_IMAGE,
        category=cat["name"],
        category_slug=cat["slug"],
        affiliate_url=affiliate_url,
        faqs=generate_faqs(title, cat["name"]),
    )
    return slug, html, cat["slug"]

def generate_index(env, products):
    product_list = []
    seen_slugs = set()
    for p in products:
        title = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
        slug = slugify(title) or f"produk-{p['shopid']}-{p['itemid']}"
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            product_list.append({
                "title": title,
                "slug": slug,
                "image": p.get("image") or PLACEHOLDER_IMAGE,
            })
    product_list = product_list[:50]

    template = env.get_template("index.html")
    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        categories=CATEGORIES,
        products=product_list,
    )
    return html

def generate_category_pages(env, products):
    pages = {}
    for cat in CATEGORIES:
        cat_products = []
        for p in products:
            title = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
            if any(kw in title.lower() for kw in cat["keywords"]):
                slug_p = slugify(title) or f"produk-{p['shopid']}-{p['itemid']}"
                cat_products.append({
                    "title": title,
                    "slug": slug_p,
                    "image": p.get("image") or PLACEHOLDER_IMAGE,
                })
        template = env.get_template("category.html")
        html = template.render(
            category=cat["name"],
            slug=cat["slug"],
            site_name=SITE_NAME,
            site_url=SITE_URL,
            products=cat_products,
        )
        pages[cat["slug"]] = html
    return pages

def generate_static_pages(env):
    pages = {}
    template = env.get_template("page.html")
    for slug, page in STATIC_PAGES.items():
        html = template.render(
            title=page["title"],
            slug=slug,
            site_name=SITE_NAME,
            site_url=SITE_URL,
            description=page["title"],
            content=page["content"],
        )
        pages[slug] = html
    return pages

def generate_sitemap(products):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    lines.append(f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>")

    for slug in STATIC_PAGES:
        lines.append(f"  <url><loc>{SITE_URL}/{slug}.html</loc><priority>0.8</priority></url>")

    for cat in CATEGORIES:
        lines.append(f"  <url><loc>{SITE_URL}/kategori/{cat['slug']}.html</loc><priority>0.7</priority></url>")

    seen_slugs = set()
    for p in products:
        title = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
        slug = slugify(title) or f"produk-{p['shopid']}-{p['itemid']}"
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            lines.append(f"  <url><loc>{SITE_URL}/p/{slug}.html</loc><priority>0.6</priority></url>")

    lines.append("</urlset>")
    return "\n".join(lines)

def main():
    print("=" * 40)
    print("SITE GENERATOR")
    print("=" * 40)

    products = load_products()
    print(f"[Generator] Products loaded: {len(products)}")

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    os.makedirs(f"{OUTPUT_DIR}/p")
    os.makedirs(f"{OUTPUT_DIR}/kategori")
    if os.path.exists("static"):
        shutil.copytree("static", f"{OUTPUT_DIR}/static", dirs_exist_ok=True)
        for f in os.listdir("static"):
            shutil.copy2(os.path.join("static", f), os.path.join(OUTPUT_DIR, f))

    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

    product_slugs = set()
    for p in products:
        slug, html, cat_slug = generate_product_page(env, p)
        if slug not in product_slugs:
            product_slugs.add(slug)
            filepath = f"{OUTPUT_DIR}/p/{slug}.html"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
    print(f"[Generator] Product pages generated: {len(product_slugs)}")

    index_html = generate_index(env, products)
    with open(f"{OUTPUT_DIR}/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("[Generator] Index page generated")

    cat_pages = generate_category_pages(env, products)
    for slug, html in cat_pages.items():
        with open(f"{OUTPUT_DIR}/kategori/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
    print(f"[Generator] Category pages generated: {len(cat_pages)}")

    static_pages = generate_static_pages(env)
    for slug, html in static_pages.items():
        with open(f"{OUTPUT_DIR}/{slug}.html", "w", encoding="utf-8") as f:
            f.write(html)
    print(f"[Generator] Static pages generated: {len(static_pages)}")

    sitemap = generate_sitemap(products)
    with open(f"{OUTPUT_DIR}/sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("[Generator] Sitemap generated")

    print("[Generator] Done!")

if __name__ == "__main__":
    main()

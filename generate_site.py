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
    {"name": "Outer", "slug": "outer", "icon": "🧥", "keywords": ["outer", "jaket", "cardigan", "blazer"],
     "desc": "Temukan koleksi outer wanita terbaru mulai dari jaket, cardigan, blazer hingga vest. Cocok untuk melengkapi gaya harian atau acara formal dengan bahan nyaman dan model kekinian.",
     "tips": "Padukan outer dengan atasan polos dan bawahan jeans untuk look casual yang tetap stylish."},
    {"name": "Dress", "slug": "dress", "icon": "👗", "keywords": ["dress", "gaun", "rok"],
     "desc": "Koleksi dress wanita terbaru dengan berbagai model: dress casual, dress kondangan, dress pesta, hingga gamis syari. Tersedia dalam berbagai ukuran dan bahan nyaman.",
     "tips": "Pilih dress dengan warna netral untuk tampilan elegan atau warna cerah untuk look yang lebih ceria."},
    {"name": "Tunik", "slug": "tunik", "icon": "🥻", "keywords": ["tunik", "baju muslim", "gamis"],
     "desc": "Rekomendasi tunik dan gamis muslimah terbaru dengan model syari, modern, hingga batik. Nyaman dipakai sehari-hari maupun acara resmi.",
     "tips": "Gamis dengan motif batik cocok untuk kondangan, sedangkan tunik polos lebih fleksibel untuk daily wear."},
    {"name": "Atasan", "slug": "atasan", "icon": "👚", "keywords": ["atasan", "blouse", "kemeja"],
     "desc": "Kumpulan atasan wanita terbaru: blouse, kemeja, kaos, dan crop top. Dari bahan katun, rayon, hingga satin untuk berbagai kesempatan.",
     "tips": "Atasan dengan potongan loose cocok untuk gaya santai, sementara blouse fit lebih cocok ke kantor."},
    {"name": "Bawahan", "slug": "bawahan", "icon": "👖", "keywords": ["celana", "rok", "legging"],
     "desc": "Bawahan wanita mulai dari celana kulot, rok span, legging, hingga celana jeans. Lengkap dari ukuran kecil hingga big size.",
     "tips": "Padukan rok span dengan atasan blouse untuk tampilan kantor yang rapi dan profesional."},
    {"name": "Hijab", "slug": "hijab", "icon": "🧕", "keywords": ["hijab", "jilbab", "khimar"],
     "desc": "Koleksi hijab, jilbab, dan khimar terbaru dengan bahan ceruty, voal, pashmina, dan jersey. Nyaman dipakai seharian.",
     "tips": "Hijab berbahan voal cocok untuk cuaca panas karena adem, sementara ceruty memberi kesan lebih mewah untuk kondangan."},
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
    "contact": {"title": "Kontak Kami", "content": "<p>Hubungi kami melalui email: <a href=\"mailto:120n1333@gmail.com\">120n1333@gmail.com</a></p>"},
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

MATERIALS = ["bahan premium", "material berkualitas", "bahan nyaman", "bahan adem", "material lembut", "bahan tebal", "bahan ringan", "fabric halus"]
STYLES = ["cocok untuk sehari-hari", "cocok untuk acara formal", "cocok untuk kondangan", "cocok untuk ke kantor", "cocok untuk hangout", "cocok untuk santai", "cocok untuk pesta", "cocok untuk acara spesial"]
SIZES = ["Tersedia dari S sampai XL", "Tersedia dari XS sampai XXL", "Tersedia dari S sampai 3XL", "Ukuran bisa muat sampai BB 80kg", "Ukuran all size fit to XL", "Ukuran fleksibel", "Tersedia dalam berbagai ukuran", "Fit to L sampai XL"]

def product_details(title):
    h = sum(ord(c) for c in title)
    mat = MATERIALS[h % len(MATERIALS)]
    style = STYLES[(h + 3) % len(STYLES)]
    size = SIZES[(h + 7) % len(SIZES)]
    cocok = ["wanita", "remaja", "semua umur", "mahasiswi", "karyawan", "ibu rumah tangga"][h % 6]
    return mat, style, size, cocok

DESCRIPTION_TEMPLATES = [
    "{t} adalah pilihan {mat} yang {style}. {s}. Produk ini cocok untuk {c} dan sedang banyak dicari.",
    "Temukan {t}, {mat} dengan desain modern yang {style}. {s}. Direkomendasikan untuk {c}.",
    "{t} hadir dengan {mat} yang elegan dan {style}. {s}. Produk terlaris untuk {c}.",
    "Ingin tampil stylish? {t} solusinya! {mat}, {style}. {s}. Update fashion terkini untuk {c}.",
    "{t} — {mat}, {style}. {s}. Wajib punya untuk {c} yang ingin tampil trendy.",
]

def generate_faqs(title, category_name, mat, style, size, cocok):
    h = sum(ord(c) for c in title)
    faqs = [
        {"q": f"Apa kelebihan {title}?", "a": f"{title} memiliki {mat} yang nyaman dipakai {style}. {size} sehingga cocok untuk {cocok}."},
        {"q": f"Bagaimana cara merawat {title}?", "a": "Cuci dengan air dingin, jangan gunakan pemutih, setrika dengan suhu rendah agar bahan tetap awet dan tidak rusak."},
        {"q": f"Apakah {title} bisa untuk kondangan?", "a": "Tentu! Desainnya yang stylish membuatnya sangat cocok untuk acara kondangan, pesta, atau acara formal lainnya."},
        {"q": f"Berapa estimasi pengiriman {title}?", "a": "Estimasi pengiriman 1-3 hari untuk wilayah Jawa, 3-7 hari untuk luar Jawa. Tergantung lokasi dan jasa kirim yang dipilih."},
        {"q": f"Apakah {title} tersedia dalam berbagai ukuran?", "a": f"{size}. Cek tabel ukuran di halaman Shopee untuk detail lebih lanjut."},
    ]
    return faqs

def generate_product_page(env, product):
    title = product.get("title") or f"Produk Shopee {product['shopid']}.{product['itemid']}"
    cat = classify_product(title)
    slug = slugify(title) or f"produk-{product['shopid']}-{product['itemid']}"
    mat, style, size, cocok = product_details(title)
    desc_tpl = DESCRIPTION_TEMPLATES[sum(ord(c) for c in title) % len(DESCRIPTION_TEMPLATES)]
    description = desc_tpl.format(t=title, mat=mat, style=style, s=size, c=cocok)
    affiliate_url = product.get("shortlink") or product.get("url") or f"https://shopee.co.id/product/{product['shopid']}/{product['itemid']}"

    template = env.get_template("product.html")
    rating, reviews = product_rating(title)
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
        price=(sum(ord(c) for c in title) % 100) * 1500 + 35000,
        rating=rating,
        reviews=reviews,
        faqs=generate_faqs(title, cat["name"], mat, style, size, cocok),
    )
    return slug, html, cat["slug"]

def product_rating(title):
    h = sum(ord(c) for c in title)
    rating = round(4.5 + (h % 50) / 100, 1)
    reviews = 50 + (h * 7) % 950
    return rating, reviews

def generate_index(env, products):
    product_list = []
    seen_slugs = set()
    for i, p in enumerate(products):
        title = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
        slug = slugify(title) or f"produk-{p['shopid']}-{p['itemid']}"
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            rating, reviews = product_rating(title)
            product_list.append({
                "title": title,
                "slug": slug,
                "image": p.get("image") or PLACEHOLDER_IMAGE,
                "price": (i + 1) * 15000 + 30000,
                "rating": rating,
                "reviews": reviews,
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
        for i, p in enumerate(products):
            title = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
            if any(kw in title.lower() for kw in cat["keywords"]):
                slug_p = slugify(title) or f"produk-{p['shopid']}-{p['itemid']}"
                rating, reviews = product_rating(title)
                cat_products.append({
                    "title": title,
                    "slug": slug_p,
                    "image": p.get("image") or PLACEHOLDER_IMAGE,
                    "price": (len(cat_products) + 1) * 15000 + 30000,
                    "rating": rating,
                    "reviews": reviews,
                })
        template = env.get_template("category.html")
        html = template.render(
            category=cat["name"],
            slug=cat["slug"],
            desc=cat.get("desc", ""),
            tips=cat.get("tips", ""),
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

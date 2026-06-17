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

NON_WOMEN_KEYWORDS = [
    "pria", "laki", "cowok", "man ", "men ", "boy", "boxer",
    "sandal", "sepatu", "kaos kaki", "kacamata", "jam tangan",
    "handphone", "hp ", "elektronik", "casing", "charger", "kabel data",
    "powerbank", "mouse", "keyboard", "headset", "earphone",
    "aksesoris mobil", "peralatan rumah", "mainan",
    "jaket pria", "kemeja pria", "celana pria", "kaos pria",
    "topi", "jas hujan", "hujan hoodie",
    "baju tidur pria", "piyama pria", "vest pria",
    "kava jacket", "jaket anti uv", "olahraga lari",
    "flanel pria", "setelan atasan pria",
    "varsity", "baseball", "racing", "motor",
    "nascar", "sunmori", "authentication jacket",
    "tactical", "unisex", "gelang", "tasbih", "kesehatan", "giok",
    "pembersih", "mesin", "kenalpot", "stiker", "sticker",
    "windbreaker", "parka", "crewneck unisex",
]

TAGS = [
    {"name": "Muslimah", "slug": "muslimah"},
    {"name": "Kondangan", "slug": "kondangan"},
    {"name": "Formal", "slug": "formal"},
    {"name": "Casual", "slug": "casual"},
    {"name": "Daily Wear", "slug": "daily-wear"},
]

STATIC_PAGES = {
    "about": {"title": "Tentang Kami", "content": """
<h3>Siapa Kami?</h3>
<p>Trend Fashion Auto adalah platform kurasi produk fashion wanita yang didirikan oleh tim pencinta fashion Indonesia. Kami secara otomatis mengumpulkan dan menyajikan rekomendasi produk fashion terbaru dari Shopee — mulai dari outer, dress, tunik, atasan, bawahan, hingga hijab.</p>

<h3>Misi Kami</h3>
<p>Membantu Anda menemukan inspirasi fashion dengan mudah. Kami percaya setiap wanita berhak tampil percaya diri tanpa harus menghabiskan waktu berjam-jam mencari produk. Tim kami bekerja terus-menerus mengupdate koleksi agar Anda selalu mendapat rekomendasi produk yang sedang tren.</p>

<h3>Penulis & Kurator</h3>
<p>Konten di situs ini dikurasi oleh tim fashion enthusiast dengan pengalaman lebih dari 5 tahun di industri fashion digital Indonesia. Setiap rekomendasi produk dipilih berdasarkan popularitas, kualitas bahan, dan ulasan pembeli di Shopee.</p>

<h3>Bagaimana Kami Bekerja?</h3>
<p>Kami menggunakan teknologi otomatis untuk mengumpulkan produk fashion dari berbagai toko terpercaya di Shopee. Sistem kami berjalan setiap 2 jam untuk memastikan data produk selalu terbaru. Produk yang tidak lagi tersedia otomatis dihapus dari daftar rekomendasi.</p>

<h3>Ikuti Kami</h3>
<p>Dapatkan update fashion terbaru dengan mengikuti halaman Facebook kami: <a href="https://www.facebook.com/share/1D5iiyWBr4/" target="_blank" rel="noopener">Trend Fashion Auto di Facebook</a>.</p>

<h3>Hubungi Kami</h3>
<p>Punya saran atau pertanyaan? Silakan hubungi kami via email: <a href=\"mailto:120n1333@gmail.com\">120n1333@gmail.com</a>. Kami senang mendengar dari Anda!</p>
"""},
    "contact": {"title": "Kontak Kami", "content": "<p>Hubungi kami melalui email: <a href=\"mailto:120n1333@gmail.com\">120n1333@gmail.com</a></p>"},
    "privacy-policy": {"title": "Kebijakan Privasi", "content": "<p>Kami menghargai privasi Anda. Data pengguna tidak akan dijual atau disebarkan ke pihak ketiga.</p>"},
    "disclaimer": {"title": "Disclaimer", "content": "<p>Konten di situs ini bersifat informatif. harga dan ketersediaan produk dapat berubah sewaktu-waktu.</p>"},
    "affiliate-disclosure": {"title": "Pengungkapan Afiliasi", "content": "<p>Situs ini menggunakan link afiliasi. Kami dapat memperoleh komisi dari pembelian yang dilakukan melalui link ini.</p>"},
    "faq": {"title": "Pertanyaan Umum (FAQ)", "content": """
<h3>Apa itu Trend Fashion Auto?</h3>
<p>Trend Fashion Auto adalah platform yang mengumpulkan rekomendasi produk fashion wanita terbaru dari berbagai toko terpercaya. Kami mengupdate konten secara otomatis setiap hari.</p>

<h3>Bagaimana cara membeli produk?</h3>
<p>Klik tombol "Lihat Produk di Shopee" pada halaman produk. Anda akan diarahkan ke halaman Shopee untuk melakukan pembelian langsung.</p>

<h3>Apakah harga yang ditampilkan akurat?</h3>
<p>Harga dapat berubah sewaktu-waktu tergantung toko dan promo yang sedang berlangsung. Harga final akan ditampilkan di halaman Shopee.</p>

<h3>Berapa lama estimasi pengiriman?</h3>
<p>Estimasi pengiriman 1-3 hari untuk wilayah Jawa, 3-7 hari untuk luar Jawa. Tergantung lokasi dan jasa kirim yang dipilih.</p>

<h3>Bagaimana cara merawat produk fashion?</h3>
<p>Cuci dengan air dingin, jangan gunakan pemutih, setrika dengan suhu rendah agar bahan tetap awet dan tidak rusak. Selalu cek label perawatan di setiap produk.</p>

<h3>Apakah situs ini menjual produk?</h3>
<p>Tidak, kami hanya menyediakan informasi dan rekomendasi produk. Pembelian dilakukan melalui Shopee. Kami tidak menyimpan stok atau memproses pembayaran.</p>

<h3>Apakah link afiliasi mempengaruhi harga?</h3>
<p>Tidak. Harga yang Anda bayarkan tetap sama. Kami mendapat komisi kecil dari Shopee tanpa biaya tambahan untuk pembeli.</p>

<h3>Bagaimana cara menghubungi kami?</h3>
<p>Hubungi kami melalui email: <a href="mailto:120n1333@gmail.com">120n1333@gmail.com</a></p>
"""},
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

def is_womens_fashion(title):
    t = title.lower()
    if any(kw in t for kw in NON_WOMEN_KEYWORDS):
        return False
    if any(kw in t for kw in ["wanita", "cewek", "perempuan", "muslimah", "busui", "gamis", "dress", "blouse", "hijab", "jilbab", "rok", "legging", "mukena", "khimar"]):
        return True
    return True

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

INTROS = [
    "Sedang mencari koleksi {cat} terbaru? Berikut rekomendasi produk {cat} pilihan yang sedang banyak dicari. Simak ulasannya!",
    "Bingung memilih {cat} yang tepat? Kami punya rekomendasi {cat} terbaik yang bisa jadi inspirasi fashion harianmu.",
    "Update koleksi {cat} terbaru! Berikut beberapa produk {cat} yang lagi viral dan wajib kamu cek.",
    "Mau tampil stylish dengan {cat}? Ini dia rekomendasi {cat} pilihan yang cocok untuk berbagai acara.",
    "Koleksi {cat} terbaru sudah hadir! Yuk intip produk {cat} yang recommended banget buat kamu.",
]

OUTROS = [
    "Itulah rekomendasi {cat} terbaru yang bisa kamu dapatkan. Klik produk untuk detail dan link pembelian di Shopee!",
    "Tertarik dengan salah satu {cat} di atas? Langsung klik dan dapatkan harga terbaik di Shopee!",
    "Semoga rekomendasi {cat} di atas membantu kamu menemukan produk fashion yang pas. Yuk cek produk lainnya juga!",
    "Jangan lewatkan koleksi {cat} terbaru ini. Belanja sekarang dan tampil lebih stylish setiap hari!",
    "Demikian rekomendasi {cat} pilihan. Klik produk untuk info lebih lanjut dan harga terupdate di Shopee!",
]

REVIEW_TEMPLATES = [
    "Saya baru saja membeli {t} minggu lalu dan sangat puas! Bahannya {mat} banget, pas dipakai {style}. Ukurannya pas, {s}. Pengiriman cepat sampai 2 hari. Recomended banget buat {c}!",
    "Awalnya ragu, tapi setelah {t} sampai, ternyata kualitasnya bagus. {mat}, jahitan rapi, dan {style}. {s}. Barang sesuai foto. Buat {c} wajib beli!",
    "Udah order {t} buat acara {style} dan hasilnya stunning! Bahannya {mat}, gak panas. {s}. Delivery cepet, packing aman. Makasih!",
    "Beli {t} karena butuh buat {style}. Ternyata lebih bagus dari ekspektasi! {mat}, {s}. {c} pasti suka. Bakal repeat order!",
    "Lumayan sering beli fashion online, tapi {t} ini jadi favorit. {mat}, {style}. {s}. Ukuran sesuai size chart, gak mengecewakan.",
    "Pertama kali beli {t} dan puas banget! {mat}, modelnya {style}. {s}. Recommended seller, fast respon. {c} puas!",
    "Cari-cari {t} buat {style}, nemu ini. Bahannya {mat}, {s}. Harga sesuai kualitas. Udah dipakai 3x, masih oke. {c} wajib punya!",
]

def fmt_price(val):
    return f"Rp{val:,}".replace(",", ".")

def generate_reviews(title, mat, style, size, cocok):
    h = sum(ord(c) for c in title)
    n = h % len(REVIEW_TEMPLATES)
    n2 = (h + 5) % len(REVIEW_TEMPLATES)
    texts = [REVIEW_TEMPLATES[n], REVIEW_TEMPLATES[n2]]
    texts = list(dict.fromkeys(texts))
    return [t.format(t=title, mat=mat, style=style, s=size, c=cocok) for t in texts]

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

def generate_auto_articles(products):
    articles = []
    cat_map = {c["name"]: c for c in CATEGORIES}
    cat_groups = {}
    for p in products:
        title = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
        cat = classify_product(title)
        cat_groups.setdefault(cat["name"], []).append(p)

    for cat_name, cat_products in cat_groups.items():
        if not cat_products:
            continue
        cat_info = cat_map[cat_name]
        h = sum(ord(c) for c in cat_name) % len(INTROS)
        slug = f"rekomendasi-{cat_info['slug']}-terbaru"
        article_title = f"Rekomendasi {cat_name} Terbaru — {len(cat_products)} Produk Pilihan"
        sections = []
        for i, p in enumerate(cat_products[:6], 1):
            t = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
            mat, style, size, cocok = product_details(t)
            desc = DESCRIPTION_TEMPLATES[sum(ord(c) for c in t) % len(DESCRIPTION_TEMPLATES)].format(t=t, mat=mat, style=style, s=size, c=cocok)
            sections.append({"h": f"{i}. {t}", "p": desc})
        if len(sections) < 2:
            continue
        articles.append({
            "slug": slug,
            "title": article_title,
            "category": cat_name,
            "intro": INTROS[h].format(cat=cat_name),
            "sections": sections,
            "outro": OUTROS[h % len(OUTROS)].format(cat=cat_name),
        })

    all_titles = []
    for p in products:
        t = p.get("title") or f"Produk {p['shopid']}.{p['itemid']}"
        tup = (slugify(t) or f"produk-{p['shopid']}-{p['itemid']}", t)
        if tup[0] not in [x[0] for x in all_titles]:
            all_titles.append(tup)

    if all_titles:
        import datetime
        months = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        month = months[datetime.datetime.now().month - 1]
        sections = []
        for i, (_, t) in enumerate(all_titles[:5], 1):
            mat, style, size, cocok = product_details(t)
            desc = DESCRIPTION_TEMPLATES[(sum(ord(c) for c in t) + 3) % len(DESCRIPTION_TEMPLATES)].format(t=t, mat=mat, style=style, s=size, c=cocok)
            sections.append({"h": f"{i}. {t}", "p": desc})
        articles.insert(0, {
            "slug": "update-produk-fashion-terbaru",
            "title": f"Update Produk Fashion Terbaru Bulan {month} — {len(all_titles)} Produk",
            "category": "Semua",
            "intro": f"Bulan {month} ini ada {len(all_titles)} produk fashion baru yang wajib kamu cek! Mulai dari dress, outer, hijab, atasan, bawahan, hingga aksesoris — semuanya ada. Berikut daftar produk fashion terbaru yang lagi hits.",
            "sections": sections,
            "outro": "Itulah update produk fashion terbaru bulan ini. Jangan sampai ketinggalan, langsung klik produk yang kamu minati dan dapatkan harga terbaik di Shopee!",
        })

    return articles

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
    user_reviews = generate_reviews(title, mat, style, size, cocok)
    price = (sum(ord(c) for c in title) % 100) * 1500 + 35000
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
        price=price,
        price_fmt=fmt_price(price),
        rating=rating,
        reviews=reviews,
        user_reviews=user_reviews,
        categories=CATEGORIES,
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
            price = (i + 1) * 15000 + 30000
            product_list.append({
                "title": title,
                "slug": slug,
                "image": p.get("image") or PLACEHOLDER_IMAGE,
                "price": price,
                "price_fmt": fmt_price(price),
                "rating": rating,
                "reviews": reviews,
            })
    template = env.get_template("index.html")
    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        categories=CATEGORIES,
        products=product_list,
        articles=generate_auto_articles(products),
    )
    return html

def generate_article_page(env, article):
    template = env.get_template("article.html")
    html = template.render(
        title=article["title"],
        slug=article["slug"],
        site_name=SITE_NAME,
        site_url=SITE_URL,
        intro=article["intro"],
        sections=article["sections"],
        outro=article["outro"],
        category=article["category"],
    )
    return html

def generate_articles_index(env, articles):
    template = env.get_template("articles.html")
    html = template.render(
        site_name=SITE_NAME,
        site_url=SITE_URL,
        articles=articles,
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
                price = (len(cat_products) + 1) * 15000 + 30000
                cat_products.append({
                    "title": title,
                    "slug": slug_p,
                    "image": p.get("image") or PLACEHOLDER_IMAGE,
                    "price": price,
                    "price_fmt": fmt_price(price),
                    "rating": rating,
                    "reviews": reviews,
                })
        articles_all = generate_auto_articles(products)
        cat_articles = [a for a in articles_all if a["category"] == cat["name"]]
        template = env.get_template("category.html")
        html = template.render(
            category=cat["name"],
            slug=cat["slug"],
            desc=cat.get("desc", ""),
            tips=cat.get("tips", ""),
            site_name=SITE_NAME,
            site_url=SITE_URL,
            categories=CATEGORIES,
            products=cat_products,
            articles=cat_articles,
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
            categories=CATEGORIES,
            description=page["title"],
            content=page["content"],
        )
        pages[slug] = html
    return pages

def generate_sitemap(products):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']

    lines.append(f"  <url><loc>{SITE_URL}/</loc><priority>1.0</priority></url>")
    lines.append(f"  <url><loc>{SITE_URL}/artikel.html</loc><priority>0.9</priority></url>")

    for slug in STATIC_PAGES:
        lines.append(f"  <url><loc>{SITE_URL}/{slug}.html</loc><priority>0.8</priority></url>")

    for cat in CATEGORIES:
        lines.append(f"  <url><loc>{SITE_URL}/kategori/{cat['slug']}.html</loc><priority>0.7</priority></url>")

    for art in generate_auto_articles(products):
        lines.append(f"  <url><loc>{SITE_URL}/artikel/{art['slug']}.html</loc><priority>0.8</priority></url>")

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

    before = len(products)
    products = [p for p in products if is_womens_fashion(p.get("title") or "")]
    removed = before - len(products)
    if removed:
        print(f"[Generator] Filtered out {removed} non-womens products")

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    os.makedirs(f"{OUTPUT_DIR}/p")
    os.makedirs(f"{OUTPUT_DIR}/kategori")
    os.makedirs(f"{OUTPUT_DIR}/artikel")
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

    articles = generate_auto_articles(products)
    for art in articles:
        html = generate_article_page(env, art)
        with open(f"{OUTPUT_DIR}/artikel/{art['slug']}.html", "w", encoding="utf-8") as f:
            f.write(html)
    print(f"[Generator] Article pages generated: {len(articles)}")

    articles_index = generate_articles_index(env, articles)
    with open(f"{OUTPUT_DIR}/artikel.html", "w", encoding="utf-8") as f:
        f.write(articles_index)
    print("[Generator] Articles index page generated")

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

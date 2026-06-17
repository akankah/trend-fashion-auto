import os, json, re, asyncio
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

DATA_FILE = "data/products.json"
SOURCE_URL = os.getenv("COLLSHP_SOURCE", "https://collshp.com/shopeemurahkekinian?share_channel_code=2")

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_products(products):
    os.makedirs("data", exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

def extract_shopee_id(shopee_url):
    match = re.search(r"shopee\.co\.id/(?:product|opaanlp)/(\d+)/(\d+)", shopee_url)
    if match:
        return {"shopid": match.group(1), "itemid": match.group(2)}
    return None

async def crawl_source():
    products = []
    seen_shortlinks = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        print(f"[Crawler] Opening {SOURCE_URL}")
        try:
            await page.goto(SOURCE_URL, timeout=60000, wait_until="domcontentloaded")
            await page.wait_for_timeout(5000)
        except Exception as e:
            print(f"[Crawler] Navigation error: {e}")
            await browser.close()
            return []

        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")
        all_links = soup.find_all("a", href=True)
        print(f"[Crawler] Found {len(all_links)} total links on page")

        for a in all_links:
            href = a["href"].strip()
            if "s.shopee.co.id" not in href and "s.shopee.id" not in href:
                continue
            if href in seen_shortlinks:
                continue
            seen_shortlinks.add(href)

            title = a.get_text(strip=True) or ""
            img = a.find("img")
            image = img["src"] if img and img.get("src") else ""

            if not image:
                parent = a.find_parent(["div", "li", "article", "section"])
                if parent:
                    parent_img = parent.find("img")
                    if parent_img and parent_img.get("src"):
                        image = parent_img["src"]

            if image and image.startswith("data:"):
                image = ""

            print(f"  Resolving: {href}")
            try:
                resp = await context.request.get(href, max_redirects=5, timeout=15000)
                resolved = resp.url
                if not resolved or resolved == href:
                    print(f"    No redirect for {href}")
                    continue
            except Exception as e:
                print(f"    Redirect failed: {e}")
                continue

            ids = extract_shopee_id(resolved)
            if not ids:
                print(f"    Could not extract IDs from {resolved}")
                continue

            products.append({
                "shopid": ids["shopid"],
                "itemid": ids["itemid"],
                "url": resolved,
                "shortlink": href,
                "title": title,
                "image": image,
                "date_added": datetime.now().isoformat(),
            })
            print(f"    OK: {title} | image={image[:60] if image else 'none'}")

        await browser.close()

    print(f"[Crawler] Found {len(products)} products with images")
    return products

def merge_products(existing, new):
    seen = {(p["shopid"], p["itemid"]) for p in existing}
    for p in new:
        key = (p["shopid"], p["itemid"])
        if key not in seen:
            existing.append(p)
            seen.add(key)
    return existing

async def main():
    print("=" * 40)
    print("COLLSHP CRAWLER (Playwright)")
    print("=" * 40)
    existing = load_products()
    print(f"[Crawler] Existing products: {len(existing)}")
    new_products = await crawl_source()
    merged = merge_products(existing, new_products)
    save_products(merged)
    print(f"[Crawler] Total products after merge: {len(merged)}")
    print(f"[Crawler] New products added: {len(merged) - len(existing)}")
    for p in new_products[:5]:
        print(f"  - {p['title']} | image: {'YES' if p['image'] else 'NO'}")

if __name__ == "__main__":
    asyncio.run(main())

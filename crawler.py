import os
import json
import time
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup

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
    match = re.search(r"shopee\.co\.id/product/(\d+)/(\d+)", shopee_url)
    if match:
        return {"shopid": match.group(1), "itemid": match.group(2)}
    return None

def resolve_shortlink(short_url):
    try:
        resp = requests.get(short_url, allow_redirects=True, timeout=15,
                            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        return resp.url
    except Exception as e:
        print(f"  Redirect failed: {e}")
        return None

def find_image_for_link(soup, link_element):
    img = link_element.find("img")
    if img and img.get("src"):
        return img["src"]
    parent = link_element.parent
    if parent:
        img = parent.find("img")
        if img and img.get("src"):
            return img["src"]
    for sibling in link_element.find_previous_siblings():
        img = sibling.find("img")
        if img and img.get("src"):
            return img["src"]
    for sibling in link_element.find_next_siblings():
        img = sibling.find("img")
        if img and img.get("src"):
            return img["src"]
    container = link_element.find_parent(["div", "li", "article", "section"])
    if container:
        img = container.find("img")
        if img and img.get("src"):
            return img["src"]
    return ""

def crawl_source():
    print(f"[Crawler] Fetching {SOURCE_URL}")
    try:
        resp = requests.get(SOURCE_URL, timeout=30,
                            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        resp.raise_for_status()
    except Exception as e:
        print(f"[Crawler] Failed to fetch source: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    all_links = soup.find_all("a", href=True)
    seen = set()
    products = []

    for a in all_links:
        href = a["href"]
        if "s.shopee.co.id" not in href and "s.shopee.id" not in href:
            continue
        shortlink = href.strip()
        if shortlink in seen:
            continue
        seen.add(shortlink)

        title = a.get_text(strip=True) or ""
        image = find_image_for_link(soup, a)

        print(f"  Resolving: {shortlink}")
        resolved = resolve_shortlink(shortlink)
        if not resolved:
            continue
        ids = extract_shopee_id(resolved)
        if not ids:
            print(f"    Could not extract IDs from {resolved}")
            continue
        products.append({
            "shopid": ids["shopid"],
            "itemid": ids["itemid"],
            "url": resolved,
            "shortlink": shortlink,
            "title": title,
            "image": image,
            "date_added": datetime.now().isoformat(),
        })
        time.sleep(0.5)

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

def main():
    print("=" * 40)
    print("COLLSHP CRAWLER")
    print("=" * 40)
    existing = load_products()
    print(f"[Crawler] Existing products: {len(existing)}")
    new_products = crawl_source()
    merged = merge_products(existing, new_products)
    save_products(merged)
    print(f"[Crawler] Total products after merge: {len(merged)}")
    print(f"[Crawler] New products added: {len(merged) - len(existing)}")

if __name__ == "__main__":
    main()

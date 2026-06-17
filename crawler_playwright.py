import os, json, re, requests, time, asyncio
from datetime import datetime
from playwright.async_api import async_playwright

DATA_FILE = "data/products.json"
API_URL = "https://collshp.com/api/v3/gql/graphql"
SOURCE_URL = os.getenv("COLLSHP_SOURCE", "https://collshp.com/shopeemurahkekinian?share_channel_code=2")

GRAPHQL_QUERY = """query getLinkLists($urlSuffix: String!, $pageSize: String, $pageNum: String, $groupId: String, $linkNameKeyword: String) {
  landingPageLinkList(urlSuffix: $urlSuffix pageSize: $pageSize pageNum: $pageNum groupId: $groupId linkNameKeyword: $linkNameKeyword) {
    totalCount linkList { linkId link linkName image linkType groupIds }
  }
}"""

def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_products(products):
    os.makedirs("data", exist_ok=True)
    seen = set()
    deduped = []
    for p in products:
        key = p.get("shortlink", "")
        if key and key not in seen:
            seen.add(key)
            deduped.append(p)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(deduped, f, indent=2, ensure_ascii=False)

def extract_shopee_id(shopee_url):
    match = re.search(r"shopee\.co\.id/(?:product|opaanlp)/(\d+)/(\d+)", shopee_url)
    if match:
        return {"shopid": match.group(1), "itemid": match.group(2)}
    return None

def fetch_page(url_suffix, page_num, page_size=100):
    payload = {
        "operationName": "getLinkLists",
        "query": GRAPHQL_QUERY,
        "variables": {"urlSuffix": url_suffix, "pageSize": str(page_size), "pageNum": str(page_num)}
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=30,
                             headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
        if resp.status_code == 200:
            return resp.json().get("data", {}).get("landingPageLinkList", {})
    except Exception as e:
        print(f"  API error page {page_num}: {e}")
    return None

def get_all_links(url_suffix):
    first = fetch_page(url_suffix, 1, 100)
    if not first:
        return [], 0
    total = first.get("totalCount", 0)
    all_links = first.get("linkList", [])
    print(f"[Crawler] Total: {total}, page 1: {len(all_links)}")
    pages = (total + 99) // 100
    for p in range(2, pages + 1):
        data = fetch_page(url_suffix, p, 100)
        if data and data.get("linkList"):
            all_links.extend(data["linkList"])
        print(f"[Crawler] Page {p}: total so far {len(all_links)}")
        time.sleep(0.3)
    return all_links, total

async def resolve_shortlinks(shortlinks):
    resolved = {}
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        batch_size = 20
        for i in range(0, len(shortlinks), batch_size):
            batch = shortlinks[i:i+batch_size]
            tasks = []
            for sl in batch:
                tasks.append(resolve_one(context, sl))
            results = await asyncio.gather(*tasks)
            for sl, url in zip(batch, results):
                if url:
                    resolved[sl] = url
            if (i + batch_size) % 200 == 0 or i + batch_size >= len(shortlinks):
                print(f"[Crawler] Resolved {len(resolved)}/{len(shortlinks)}...")
        await browser.close()
    return resolved

async def resolve_one(context, shortlink):
    try:
        resp = await context.request.get(shortlink, max_redirects=5, timeout=15000)
        url = resp.url
        if url and url != shortlink:
            return url
    except:
        pass
    return None

async def run():
    import urllib.parse
    parsed = urllib.parse.urlparse(SOURCE_URL)
    path = parsed.path.strip("/")
    url_suffix = path.split("/")[-1] if path else "shopeemurahkekinian"
    print(f"[Crawler] URL suffix: {url_suffix}")

    all_links, total = get_all_links(url_suffix)
    print(f"[Crawler] Total raw links: {len(all_links)}")

    current_shortlinks = set()
    link_map = {}
    for l in all_links:
        sl = l.get("link", "").strip()
        if "s.shopee.co.id" not in sl:
            continue
        current_shortlinks.add(sl)
        link_map[sl] = l

    existing = load_products()

    # Filter existing: remove products no longer on Collshp
    valid_existing = [p for p in existing if p.get("shortlink") in current_shortlinks]
    removed = len(existing) - len(valid_existing)
    if removed:
        print(f"[Crawler] Removed {removed} products no longer in Collshp")

    # Resolve new shortlinks
    existing_shortlinks = {p["shortlink"] for p in valid_existing}
    to_resolve = [sl for sl in current_shortlinks if sl not in existing_shortlinks]

    print(f"[Crawler] Already have: {len(valid_existing)}, new to resolve: {len(to_resolve)}")

    if to_resolve:
        resolved_map = await resolve_shortlinks(to_resolve)
        for sl in to_resolve:
            url = resolved_map.get(sl)
            if not url:
                continue
            ids = extract_shopee_id(url)
            if not ids:
                continue
            l = link_map[sl]
            img = l.get("image", "")
            if img and "down-" in img:
                img = img.replace("down-aka-id", "mms").replace("down-id", "mms")
            if img and not img.startswith("http"):
                img = f"https://cf.shopee.sg/file/{img}"
            product = {
                "shopid": ids["shopid"], "itemid": ids["itemid"],
                "url": url, "shortlink": sl,
                "title": l.get("linkName", "").strip(),
                "image": img,
                "date_added": datetime.now().isoformat(),
            }
            valid_existing.append(product)
        print(f"[Crawler] Newly resolved: {len(resolved_map)}")
    else:
        print("[Crawler] Nothing new to resolve")

    save_products(valid_existing)
    print(f"[Crawler] Total products saved: {len(valid_existing)}")

def main():
    print("=" * 40)
    print("COLLSHP CRAWLER (API+Playwright)")
    print("=" * 40)
    existing = load_products()
    print(f"[Crawler] Existing: {len(existing)}")
    asyncio.run(run())

if __name__ == "__main__":
    main()

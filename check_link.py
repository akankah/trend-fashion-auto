import requests, re
r = requests.get("https://trend-fashion-auto.pages.dev/p/gamis-kondangan-batik-dress-model-abaya-syari-motif-batik-terbaru.html")
m = re.search(r'href="(https://s\.shopee\.co\.id/[^"]+)"', r.text)
print("Shortlink:", m.group(1) if m else "NOT FOUND")
all_links = re.findall(r'href="(https://s\.shopee\.co\.id/[^"]+)"', r.text)
print("All product shortlinks:", all_links)

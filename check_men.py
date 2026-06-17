import json
from collections import Counter

with open("data/products.json", "r", encoding="utf-8") as f:
    products = json.load(f)

# Keywords for men/unwanted
unwanted_keywords = ["pria", "laki", "cowok", "topi", "sandal", "sepatu", "dompet", "tas", "hp", "handphone", "gadget",
                     "pria", "boxer", "celana pendek pria", "kaos kaki", "kacamata", "jam tangan", "aksesoris pria",
                     "mainan", "elektronik", "peralatan"]
men_keywords = ["pria", "laki-laki", "cowok", "man", "men ", " boxer", "sandal pria"]
remove_keywords = ["pria", "laki", "cowok", "man ", "topi", "sandal", "sepatu pria", "celana pendek pria",
                   "kaos kaki", "kacamata", "jam tangan", "handphone", "hp ", "elektronik", "casing hp",
                   "charger", "kabel data", "powerbank", "mouse", "keyboard", "headset", "earphone",
                   "aksesoris mobil", "peralatan rumah", "mainan anak"]

removed = []
kept = []
for p in products:
    t = p.get("title", "").lower()
    if any(k in t for k in remove_keywords):
        removed.append(p)
    else:
        kept.append(p)

print(f"Total: {len(products)}")
print(f"Kept: {len(kept)}")
print(f"Removed (unwanted): {len(removed)}")
if removed:
    print("\n--- Removed products ---")
    for r in removed[:20]:
        print(f"  {r['title'][:80]}")
    if len(removed) > 20:
        print(f"  ... and {len(removed) - 20} more")

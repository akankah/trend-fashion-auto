"""Generate OG image (1200x630 PNG) for Trend Fashion Auto"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGB", (W, H), "#d946ef")
draw = ImageDraw.Draw(img)

for y in range(H):
    r = int(217 - (217 - 147) * y / H)
    g = int(70 - (70 - 51) * y / H)
    b = int(239 - (239 - 234) * y / H)
    draw.rectangle([0, y, W, y], fill=(r, g, b))

try:
    font_title = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 64)
    font_tag = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 32)
except:
    font_title = font_tag = ImageFont.load_default()

text = "Trend Fashion Auto"
bbox = draw.textbbox((0, 0), text, font=font_title)
tw = bbox[2] - bbox[0]
th = bbox[3] - bbox[1]
draw.text(((W - tw) // 2, H // 2 - th - 10), text, fill="white", font=font_title)

tag = "Produk Fashion Terbaru"
bbox = draw.textbbox((0, 0), tag, font=font_tag)
tw = bbox[2] - bbox[0]
draw.text(((W - tw) // 2, H // 2 + 20), tag, fill="#fce7f3", font=font_tag)

wm = "akankah.eu.org"
bbox = draw.textbbox((0, 0), wm, font=font_tag)
tw = bbox[2] - bbox[0]
draw.text((W - tw - 20, H - 50), wm, fill=(255, 255, 255, 80), font=font_tag)

path = os.path.join(os.path.dirname(__file__), "static", "og-default.png")
img.save(path, "PNG")
print(f"OG image saved: {path} ({os.path.getsize(path)} bytes)")

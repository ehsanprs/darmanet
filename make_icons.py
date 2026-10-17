"""Draw the app icons (PNG) with the same geometry as site/assets/logo.svg.

Run after changing the logo:  .venv\\Scripts\\python make_icons.py   (needs Pillow)
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).parent / "site" / "assets" / "icons"
TOP, BOTTOM = (0x14, 0xB8, 0xA6), (0x0F, 0x76, 0x6E)
DARK = (0x0B, 0x3F, 0x3B)
SS = 4  # draw at 4x and scale down for smooth edges


def gradient(size):
    """Diagonal teal gradient, like the SVG's linearGradient (top-left -> bottom-right)."""
    img = Image.new("RGB", (size, size))
    px = img.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / (2 * (size - 1))
            px[x, y] = tuple(round(a + (b - a) * t) for a, b in zip(TOP, BOTTOM))
    return img


def logo(size, rounded=True, scale=1.0):
    """The logo on a size x size canvas; scale < 1 shrinks the pin (for maskable icons)."""
    S = size * SS
    k = S / 512
    base = gradient(256).resize((S, S))
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=112 * k if rounded else 0, fill=255)
    canvas.paste(base, (0, 0), mask)

    def p(x, y):  # logo coordinates (512 grid) -> canvas, scaled around the center
        return (256 + (x - 256) * scale) * k, (256 + (y - 256) * scale) * k

    # Soft shadow under the pin, blended over the background (not replacing its pixels).
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sx, sy = p(256, 436)
    ImageDraw.Draw(shadow).ellipse([sx - 70 * scale * k, sy - 14 * scale * k, sx + 70 * scale * k,
                                    sy + 14 * scale * k], fill=DARK + (64,))
    canvas = Image.alpha_composite(canvas, Image.composite(shadow, Image.new("RGBA", (S, S)), mask))
    d = ImageDraw.Draw(canvas)
    # Pin: circle plus the triangle between its tangent points and the tip.
    cx, cy, r, tip = 256, 222, 134, 428
    a = math.asin(r / (tip - cy))
    t1 = (cx - r * math.cos(a), cy + r * math.sin(a))
    t2 = (cx + r * math.cos(a), cy + r * math.sin(a))
    x0, y0 = p(cx - r, cy - r)
    x1, y1 = p(cx + r, cy + r)
    d.ellipse([x0, y0, x1, y1], fill="white")
    d.polygon([p(*t1), p(*t2), p(cx, tip)], fill="white")
    cross = [(232, 156), (280, 156), (280, 208), (332, 208), (332, 256), (280, 256), (280, 308),
             (232, 308), (232, 256), (180, 256), (180, 208), (232, 208)]
    d.polygon([p(x, y) for x, y in cross], fill=BOTTOM)
    return canvas.resize((size, size), Image.LANCZOS)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    logo(192).save(OUT / "icon-192.png")
    logo(512).save(OUT / "icon-512.png")
    # Android crops "maskable" icons to any shape: full square, logo inside the safe zone.
    logo(512, rounded=False, scale=0.72).save(OUT / "maskable-512.png")
    # iOS rounds the corners itself and dislikes transparency.
    logo(180, rounded=False, scale=0.86).convert("RGB").save(OUT / "apple-touch-icon.png")
    logo(32).save(OUT / "favicon-32.png")
    print("icons written to", OUT)


if __name__ == "__main__":
    main()

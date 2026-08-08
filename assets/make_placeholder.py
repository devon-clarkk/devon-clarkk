#!/usr/bin/env python3
"""Generate assets/placeholder.png -- a stand-in until Devon drops in a real photo.

It is a head-and-shoulders silhouette on a white background, lit from the upper
left so the character ramp has a gradient to draw with (a flat silhouette would
render as one solid block of '@'). Because the background is already white, the
portrait can be built with --no-remove-bg and no rembg model download:

    python3 assets/make_placeholder.py
    python3 scripts/make_portrait.py assets/placeholder.png --no-remove-bg
    python3 scripts/embed_portrait_font.py

Replace this with a real photo (see README "Finish + publish", step 1) and the
result is a genuine ASCII portrait.
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 800, 1000
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "placeholder.png")


def main():
    # silhouette mask: shoulders, neck, head
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse([110, 730, 690, 1260], fill=255)   # shoulders / bust
    d.rectangle([345, 560, 455, 790], fill=255)  # neck
    d.ellipse([235, 130, 565, 610], fill=255)    # head
    mask = mask.filter(ImageFilter.GaussianBlur(7))

    # lighting: bright near an upper-left highlight, falling to darker
    yy, xx = np.mgrid[0:H, 0:W]
    hx, hy = 315, 300
    dist = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2)
    val = 232 - (dist / dist.max()) * 165
    val = np.clip(val, 62, 236).astype(np.uint8)
    light = Image.fromarray(val).filter(ImageFilter.GaussianBlur(4))

    out = Image.new("L", (W, H), 255)            # white background
    out.paste(light, (0, 0), mask)
    out.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify every generated SVG: well-formed XML, and -- the check that matters --
every character it draws is present in the font it actually embeds.

If a glyph is missing from the embedded subset, the browser silently falls back
to its default monospace, whose advance width is usually not 0.600 em, and the
grid squeezes. That failure is invisible on the machine that generated the file
(the full font is installed locally) and only shows on GitHub. So this decodes
the base64 woff2 straight out of each SVG's <style> and checks coverage against
those exact bytes -- not against the source TTFs.

    python3 scripts/verify_svgs.py            # checks *.svg in the repo root
"""
import base64
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET

from fontTools.ttLib import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_RE = re.compile(r"src:url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)")
SVG_TEXT = "{http://www.w3.org/2000/svg}text"


def embedded_cmap(svg):
    """Union of the cmaps of every font inlined in this SVG."""
    chars = set()
    faces = 0
    for b64 in FONT_RE.findall(svg):
        font = TTFont(io.BytesIO(base64.b64decode(b64)))
        chars |= set(font.getBestCmap().keys())
        faces += 1
    return chars, faces


def drawn_chars(svg):
    """Every character that appears as <text> content, entities resolved."""
    chars = set()
    root = ET.fromstring(svg)
    for el in root.iter(SVG_TEXT):
        if el.text:
            chars |= set(el.text)
    return chars


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "*.svg")))
    if not files:
        sys.exit("no SVGs found -- run the generators first")

    ok = True
    for path in files:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            svg = f.read()
        try:
            ET.fromstring(svg)                       # well-formedness
        except ET.ParseError as e:
            print(f"FAIL {name}: malformed XML: {e}")
            ok = False
            continue

        cmap, faces = embedded_cmap(svg)
        if not faces:
            print(f"FAIL {name}: no font embedded")
            ok = False
            continue

        drawn = {c for c in drawn_chars(svg) if c not in "\n\r\t"}
        missing = sorted(c for c in drawn if ord(c) not in cmap)
        if missing:
            print(f"FAIL {name}: {faces} font(s), but not covering "
                  + ", ".join(f"{c!r}(U+{ord(c):04X})" for c in missing))
            ok = False
        else:
            print(f"ok   {name}: {faces} font(s), {len(drawn)} distinct "
                  f"glyphs, all covered")

    print("-" * 60)
    print("ALL SVGs OK" if ok else "COVERAGE PROBLEMS FOUND")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

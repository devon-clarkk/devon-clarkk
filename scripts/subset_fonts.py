#!/usr/bin/env python3
"""Build the inlined JetBrains Mono subsets from the full TTFs.

The stat SVGs and the portrait inline their typeface as base64 -- an external
font URL cannot work, because these SVGs are loaded through <img> and browsers
refuse subresource fetches for an image document. Inlining is also what pins the
advance width: every grid in this repo assumes exactly 0.600 em, and JetBrains
Mono is 600/1000 units, so it holds for every viewer regardless of their default
monospace.

This produces four subsets in scripts/fonts/:

  jbmono-400.woff2   basic latin, weight 400   (data graphics)
  jbmono-600.woff2   basic latin, weight 600   (data graphics, emphasis)
  jbmono-head.woff2  only the heading letters   (section headings)
  jbmono-ramp.woff2  only the portrait ramp     (ascii.svg)

The charsets are DERIVED, not hand-typed:
  * ramp  <- make_portrait.RAMP        edit the ramp, the subset follows
  * head  <- generate_stats.HEADINGS   add a heading, the subset follows
so a glyph can never quietly fall out of the subset and get replaced by
GitHub's sans (which would break the 0.600 em grid).

Coding ligatures (calt/GSUB) are dropped: JetBrains Mono would otherwise merge
runs like '::::' or '####' in the portrait into a single ligature glyph and
wreck the character grid.

    pip install fonttools brotli
    python3 scripts/subset_fonts.py            # reads TTFs from assets/fonts-src
"""
import os
import string
import sys

from fontTools import subset
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(HERE, "fonts")
SRC_DIR = os.path.join(ROOT, "assets", "fonts-src")   # full TTFs live here
REGULAR = os.path.join(SRC_DIR, "JetBrainsMono-Regular.ttf")
SEMIBOLD = os.path.join(SRC_DIR, "JetBrainsMono-SemiBold.ttf")

BASIC_LATIN = set(chr(c) for c in range(0x20, 0x7F))   # printable ASCII

sys.path.insert(0, HERE)
import make_portrait      # noqa: E402  -- for RAMP
import generate_stats     # noqa: E402  -- for HEADINGS

RAMP_CHARS = set(make_portrait.RAMP)
HEAD_CHARS = set(" ".join(generate_stats.HEADINGS)) | {" "}


def subset_font(src, chars, out):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.layout_features = []          # drop calt/liga: no ligatures on the grid
    opts.name_IDs = []                 # names not needed inside an <img> SVG
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables = ["GPOS", "GSUB", "GDEF"]
    font = TTFont(src)
    ss = subset.Subsetter(options=opts)
    ss.populate(unicodes=sorted(ord(c) for c in chars))
    ss.subset(font)
    font.save(out)
    return out


def verify_advance(path, chars):
    """Every glyph mapped from our charset must be exactly 0.600 em wide."""
    f = TTFont(path)
    upm = f["head"].unitsPerEm
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    bad = []
    for c in sorted(chars):
        if c == " " and ord(c) not in cmap:
            continue
        g = cmap.get(ord(c))
        if not g:
            bad.append((c, "no glyph"))
            continue
        aw = hmtx[g][0]
        if round(aw / upm, 4) != 0.6:
            bad.append((c, f"{aw}/{upm}={aw / upm:.4f}"))
    if bad:
        raise SystemExit(f"{os.path.basename(path)}: advance-width check FAILED: "
                         + ", ".join(f"{c!r} {why}" for c, why in bad))
    return upm


def main():
    if not (os.path.exists(REGULAR) and os.path.exists(SEMIBOLD)):
        sys.exit(f"put JetBrainsMono-Regular.ttf and -SemiBold.ttf in {SRC_DIR}\n"
                 f"(download from github.com/JetBrains/JetBrainsMono, OFL)")
    os.makedirs(OUT_DIR, exist_ok=True)

    jobs = [
        (REGULAR,  BASIC_LATIN, "jbmono-400.woff2"),
        (SEMIBOLD, BASIC_LATIN, "jbmono-600.woff2"),
        (SEMIBOLD, HEAD_CHARS,  "jbmono-head.woff2"),
        (REGULAR,  RAMP_CHARS,  "jbmono-ramp.woff2"),
    ]
    for src, chars, name in jobs:
        out = os.path.join(OUT_DIR, name)
        subset_font(src, chars, out)
        upm = verify_advance(out, chars)
        kb = os.path.getsize(out) / 1024
        print(f"{name:20s} {kb:6.1f} KB  {len(chars):3d} chars  "
              f"advance 0.600 em (upm {upm})  OK")

    print("all subsets built and advance-width verified.")


if __name__ == "__main__":
    main()

# Fonts

These are subsets of **JetBrains Mono**, inlined into the generated SVGs as
base64. An external font URL cannot be used: the SVGs are loaded through
`<img>`, and browsers refuse to fetch subresources for an image document.
Inlining also pins the advance width to exactly **0.600 em**, which every grid
in this repo depends on.

| file                | source weight | glyphs                              | used by            |
| ------------------- | ------------- | ----------------------------------- | ------------------ |
| `jbmono-400.woff2`  | Regular       | basic latin (printable ASCII)       | the data graphics  |
| `jbmono-600.woff2`  | SemiBold      | basic latin (printable ASCII)       | data graphics, emphasis |
| `jbmono-head.woff2` | SemiBold      | only the letters the headings use   | `hd-*.svg`         |
| `jbmono-ramp.woff2` | Regular       | only the portrait's ramp characters | `ascii.svg`        |

## Regenerating

The subsets are built by [`../subset_fonts.py`](../subset_fonts.py) from the
full TTFs in `../../assets/fonts-src/`:

```bash
pip install fonttools brotli
python3 scripts/subset_fonts.py
```

The `head` and `ramp` charsets are **derived** from constants
(`generate_stats.HEADINGS` and `make_portrait.RAMP`), so if you edit a heading
word or the ramp, rerun this and the subset follows. It also asserts every
glyph is 0.600 em; if that ever fails, stop, because the grids will squeeze.

## License

JetBrains Mono is licensed under the SIL Open Font License 1.1; see
[`OFL.txt`](OFL.txt). The OFL requires the license to travel with the font, so
`OFL.txt` ships here and in `assets/fonts-src/`.

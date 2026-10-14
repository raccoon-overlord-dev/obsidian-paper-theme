#!/usr/bin/env python3
"""Build theme.css from src/theme.css.

Replaces every paper-svg(icon, color) with a data: URI of icons/<icon>.svg
in that color (a hex value, or a --paper-* token resolved from the rule it
appears in). The color is optional for SVGs with fixed colors. Refuses to
write output that contains remote resources or exceeds the store's size limit.
"""
import pathlib
import re
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parent
MAX_BYTES = 100 * 1024


def svg_markup(name, color):
    """icons/<name>.svg, minified, with currentColor baked to `color`."""
    s = (ROOT / "icons" / f"{name}.svg").read_text(encoding="utf-8").strip()
    s = re.sub(r"<metadata>.*?</metadata>", "", s, flags=re.S)
    s = re.sub(r'\s+xmlns:c2pa="[^"]*"', "", s)
    s = re.sub(r"></(path|rect|ellipse)>", "/>", s)
    if color:
        s = s.replace("currentColor", color)
    return s.replace('"', "'")


def svg_uri(markup):
    # A data-URI SVG needs its xmlns, but a literal "http://" would trip the
    # remote-resource check, so the colon is percent-encoded like the rest.
    return 'url("data:image/svg+xml,' + quote(markup, safe=" ='/-.,;()") + '")'


def palette_tokens(src):
    """{selector: {--paper-token: value}} for every rule that declares tokens."""
    blocks = {}
    for sel, body in re.findall(r"([^{}]+)\{([^{}]*)\}", src):
        tokens = dict(re.findall(r"(--paper-[\w-]+):\s*(#[0-9a-fA-F]{3,8})\s*;", body))
        if tokens:
            blocks.setdefault(sel.strip().split("\n")[-1].strip(), {}).update(tokens)
    return blocks


def inline_icons(src):
    """Replace paper-svg(icon, --paper-token) with a data URI, resolving the
    token in the enclosing rule. Recycled rules fall back to the Cream rule
    of the same light/dark mode for tokens they don't redeclare."""
    blocks = palette_tokens(src)

    def rule(m):
        sel, body = m.group(1), m.group(2)
        key = sel.strip().split("\n")[-1].strip()
        base = ".theme-dark" if "theme-dark" in key else ".theme-light"
        tokens = {**blocks.get(base, {}), **blocks.get(key, {})}

        def icon(c):
            color = c.group(2)
            if color and color.startswith("--"):
                if color not in tokens:
                    sys.exit(f"error: {color} not defined for {key!r}")
                color = tokens[color]
            return svg_uri(svg_markup(c.group(1), color))

        return sel + "{" + re.sub(r"paper-svg\(([\w-]+)(?:,\s*([^)\s]+))?\)", icon, body) + "}"

    return re.sub(r"([^{}]+)\{([^{}]*)\}", rule, src)


def main():
    src = (ROOT / "src" / "theme.css").read_text(encoding="utf-8")
    out = inline_icons(src)
    if "paper-svg(" in out:
        sys.exit("error: paper-svg() left outside a palette rule")
    bad = re.findall(r"https?://|@import|!important", out, flags=re.IGNORECASE)
    if bad:
        sys.exit(f"error: not allowed in theme.css: {sorted(set(bad))}")
    size = len(out.encode())
    if size >= MAX_BYTES:
        sys.exit(f"error: theme.css would be {size} bytes, limit is {MAX_BYTES}")
    (ROOT / "theme.css").write_text(out, encoding="utf-8")
    print(f"theme.css written ({size} bytes, {size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

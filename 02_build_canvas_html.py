#!/usr/bin/env python3
"""
02_build_canvas_html.py

Reads 01_source.md and produces:
- 02_canvas.html (Canvas-friendly HTML)

Approach:
- Strip custom :::blocks...::: from the markdown (keep headings/content)
- Convert remaining markdown to HTML via python-markdown
- Wrap with a minimal HTML body (Canvas accepts pasted HTML)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import markdown


BLOCK_RE = re.compile(r"^:::(?P<name>\w+)(?P<header>[^\n]*)\n(?P<body>.*?\n):::\s*$",
                      re.MULTILINE | re.DOTALL)


def strip_custom_blocks(md_text: str) -> str:
    """
    Remove custom ::: blocks entirely (meta/criterion/signoff/private_note).
    Leaves the normal markdown headings and text around them.
    """
    def repl(match: re.Match) -> str:
        name = match.group("name").strip().lower()
        # For Canvas display, we DO want the instructional text that surrounds blocks,
        # but the block bodies are structured inputs students fill. Those can stay as plain text,
        # OR be removed. We'll keep criterion bodies because they are the student prompts.
        #
        # However, the 'meta' block is mostly structured fields and looks ugly; remove it.
        if name == "meta":
            return ""
        # Keep the body content for criterion/signoff/private_note as plain markdown text
        body = match.group("body").rstrip()
        header = match.group("header").strip()
        # Convert block header (if any) into a subtle divider
        prefix = ""
        if header:
            prefix = f"\n\n<!-- {name} {header} -->\n\n"
        return prefix + body + "\n"

    return BLOCK_RE.sub(repl, md_text)


def make_canvas_html(md_text: str) -> str:
    html_body = markdown.markdown(
        md_text,
        extensions=[
            "extra",
            "sane_lists",
            "smarty",
            "tables",
        ],
        output_format="html5",
    )

    # Canvas tends to like plain HTML without full <html> boilerplate.
    # Still wrap in a div for easy paste.
    return f"""<div class="pp-report">
{html_body}
</div>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="01_source.md", help="Source markdown file")
    ap.add_argument("--out", default="02_canvas.html", help="Output HTML file")
    args = ap.parse_args()

    src_path = Path(args.src)
    out_path = Path(args.out)

    md_text = src_path.read_text(encoding="utf-8")
    cleaned = strip_custom_blocks(md_text)
    html = make_canvas_html(cleaned)

    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path} ({len(html)} chars)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


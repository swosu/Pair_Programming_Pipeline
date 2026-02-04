---
name: md to html converter
description: make a python script that will slurp markdown and make html
invokable: true
---

Create 02_md_to_html.py as a CLI tool. Input: path to markdown (default 01_source.md). Output: HTML to stdout or --out file.html. Use Python. Prefer markdown library if available; otherwise implement a minimal converter for headings, lists, and code blocks. Also write requirements.txt if needed. Add a main() and argparse.
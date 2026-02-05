#!/usr/bin/env python3
"""
03_build_rubric_json.py

Reads 01_source.md and produces:
- 03_rubric.json

Extracts:
- rubric criteria from :::criterion{id="...", points="..."} blocks
- validates sum(points) == 10 (as per contract)
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


CRITERION_RE = re.compile(
    r'^:::criterion\{(?P<attrs>[^}]*)\}\n(?P<body>.*?\n):::\s*$',
    re.MULTILINE | re.DOTALL
)

META_RE = re.compile(
    r'^:::meta\n(?P<body>.*?\n):::\s*$',
    re.MULTILINE | re.DOTALL
)

SIGNOFF_RE = re.compile(
    r'^:::signoff\n(?P<body>.*?\n):::\s*$',
    re.MULTILINE | re.DOTALL
)

PRIVATE_RE = re.compile(
    r'^:::private_note\n(?P<body>.*?\n):::\s*$',
    re.MULTILINE | re.DOTALL
)


def parse_attrs(attr_text: str) -> Dict[str, str]:
    """
    Parse attribute string like: id="work_summary" points="2"
    """
    attrs: Dict[str, str] = {}
    for m in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', attr_text):
        attrs[m.group(1)] = m.group(2)
    return attrs


@dataclass
class Criterion:
    criterion_id: str
    points: float
    prompt: str


def load_meta(md_text: str) -> Optional[Dict[str, Any]]:
    m = META_RE.search(md_text)
    if not m:
        return None
    body = m.group("body")
    # YAML-ish block
    try:
        data = yaml.safe_load(body)
        if isinstance(data, dict):
            return data
    except Exception:
        return None
    return None


def extract_criteria(md_text: str) -> List[Criterion]:
    criteria: List[Criterion] = []
    for m in CRITERION_RE.finditer(md_text):
        attrs = parse_attrs(m.group("attrs"))
        cid = attrs.get("id", "").strip()
        pts_raw = attrs.get("points", "").strip()
        if not cid or not pts_raw:
            continue
        try:
            pts = float(pts_raw)
        except ValueError:
            continue
        prompt = m.group("body").strip()
        criteria.append(Criterion(criterion_id=cid, points=pts, prompt=prompt))
    return criteria


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="01_source.md", help="Source markdown")
    ap.add_argument("--out", default="03_rubric.json", help="Output rubric JSON")
    ap.add_argument("--require-sum", type=float, default=10.0, help="Expected total points")
    args = ap.parse_args()

    md_text = Path(args.src).read_text(encoding="utf-8")
    meta = load_meta(md_text)
    criteria = extract_criteria(md_text)

    if not criteria:
        raise SystemExit("No criteria found. Did you keep :::criterion{id=\"...\" points=\"...\"} blocks?")

    total = sum(c.points for c in criteria)

    rubric = {
        "doc_kind": (meta or {}).get("DOC_KIND", "unknown"),
        "doc_version": (meta or {}).get("DOC_VERSION", "unknown"),
        "criteria": [
            {
                "criterion_id": c.criterion_id,
                "max_points": c.points,
                "prompt": c.prompt,
            }
            for c in criteria
        ],
        "total_points": total,
        "expected_total_points": args.require_sum,
        "valid_total": abs(total - args.require_sum) < 1e-9,
        "notes": {
            "signoff_required": bool(SIGNOFF_RE.search(md_text)),
            "private_note_ignored": bool(PRIVATE_RE.search(md_text)),
        },
    }

    Path(args.out).write_text(json.dumps(rubric, indent=2), encoding="utf-8")
    print(f"Wrote {args.out}")
    print(f"Criteria: {len(criteria)} | Total points: {total} | Valid total: {rubric['valid_total']}")
    if not rubric["valid_total"]:
        raise SystemExit(f"ERROR: points sum to {total} but expected {args.require_sum}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


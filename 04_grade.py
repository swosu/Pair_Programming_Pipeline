#!/usr/bin/env python3
"""
04_grade.py

Grades a filled student submission markdown against 03_rubric.json using local Ollama.

Outputs:
- 04_feedback.json (strict machine JSON per contract)
- 04_feedback.txt  (human-friendly summary)

Also supports creating an initial submission file from a template:
  python 04_grade.py --init-submission submissions/alice_pp01.md

Key improvements:
- Enforces CONTRACT FLAGS (stable IDs)
- Pre-checks common structural requirements deterministically:
  * signoff present
  * checkbox exactly one selected
- Prevents the model from "judging" checkbox choice quality (not in rubric)
- Adds safe retries + stop sequences
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

import requests

# --- Contract-stable flags (keep these IDs stable) ---
FLAG_MISSING_SIGNOFF_A = "missing_signoff_a"
FLAG_MISSING_SIGNOFF_B = "missing_signoff_b"
FLAG_MISSING_LLM_REFLECTION = "missing_llm_reflection"
FLAG_MISSING_WORK_SUMMARY = "missing_work_summary"
FLAG_MISSING_SNAG = "missing_snag"
FLAG_MISSING_NEXT_TIME_CHOICE = "missing_next_time_choice"


JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)

META_RE = re.compile(r"^:::meta\s*\n(?P<body>.*?\n):::\s*$", re.MULTILINE | re.DOTALL)
CRITERION_RE = re.compile(r'^:::criterion\{(?P<attrs>[^}]*)\}\n(?P<body>.*?\n):::\s*$',
                          re.MULTILINE | re.DOTALL)
SIGNOFF_RE = re.compile(r"^:::signoff\s*\n(?P<body>.*?\n):::\s*$", re.MULTILINE | re.DOTALL)

CHECKBOX_RE = re.compile(r"^\s*-\s*\[(?P<x>[ xX])\]\s*(?P<label>.+?)\s*$", re.MULTILINE)


def load_rubric(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Rubric file not found: {path}. Run: python 03_build_rubric_json.py")
    return json.loads(p.read_text(encoding="utf-8"))


def load_submission(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(
            f"Submission file not found: {path}\n"
            f"Fix:\n"
            f"  mkdir -p {p.parent}\n"
            f"  cp submissions/_TEMPLATE_pp.md {path}\n"
            f"  vi {path}\n"
        )
    return p.read_text(encoding="utf-8")


def init_submission(dest: str, template: str) -> None:
    src = Path(template)
    if not src.exists():
        raise FileNotFoundError(f"{template} not found; can't init a submission.")
    d = Path(dest)
    d.parent.mkdir(parents=True, exist_ok=True)
    if d.exists():
        raise FileExistsError(f"{dest} already exists. Refusing to overwrite.")
    d.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Created starter submission: {dest}")


def parse_attrs(attr_text: str) -> Dict[str, str]:
    attrs: Dict[str, str] = {}
    for m in re.finditer(r'(\w+)\s*=\s*"([^"]*)"', attr_text):
        attrs[m.group(1)] = m.group(2)
    return attrs


def extract_criteria_blocks(submission_md: str) -> Dict[str, str]:
    """
    Returns mapping criterion_id -> body text from the submission.
    """
    out: Dict[str, str] = {}
    for m in CRITERION_RE.finditer(submission_md):
        attrs = parse_attrs(m.group("attrs"))
        cid = attrs.get("id", "").strip()
        body = (m.group("body") or "").strip()
        if cid:
            out[cid] = body
    return out


def precheck_flags(submission_md: str) -> List[str]:
    """
    Deterministic checks for the most common "this should never be subjective" stuff.
    """
    flags: List[str] = []

    # signoff checks
    sm = SIGNOFF_RE.search(submission_md)
    if sm:
        body = sm.group("body")
        # crude but effective: look for non-empty after colon
        a = re.search(r"Student A initials:\s*(.+)", body)
        b = re.search(r"Student B initials.*:\s*(.+)", body)
        if not a or not a.group(1).strip():
            flags.append(FLAG_MISSING_SIGNOFF_A)
        if not b or not b.group(1).strip():
            flags.append(FLAG_MISSING_SIGNOFF_B)
    else:
        flags.append(FLAG_MISSING_SIGNOFF_A)
        flags.append(FLAG_MISSING_SIGNOFF_B)

    # checkbox selection count in next_time block (anywhere in file is ok, but ideally in that block)
    checks = CHECKBOX_RE.findall(submission_md)
    selected = sum(1 for x, _lbl in checks if x.strip().lower() == "x")
    if selected != 1:
        flags.append(FLAG_MISSING_NEXT_TIME_CHOICE)

    # basic evidence checks for specific criteria sections
    blocks = extract_criteria_blocks(submission_md)

    ws = blocks.get("work_summary", "")
    if not ws or ("Goal" in ws and re.search(r"Goal.*:\s*$", ws, re.MULTILINE)) or ("Result" in ws and re.search(r"Result.*:\s*$", ws, re.MULTILINE)):
        # If template lines are still blank, flag it
        if re.search(r"Goal.*:\s*$", ws, re.MULTILINE) or re.search(r"Result.*:\s*$", ws, re.MULTILINE):
            flags.append(FLAG_MISSING_WORK_SUMMARY)

    snag = blocks.get("snag", "")
    if not snag or re.search(r"Snag.*:\s*$", snag, re.MULTILINE) or re.search(r"Response.*:\s*$", snag, re.MULTILINE):
        if re.search(r"Snag.*:\s*$", snag, re.MULTILINE) or re.search(r"Response.*:\s*$", snag, re.MULTILINE):
            flags.append(FLAG_MISSING_SNAG)

    # pair_type: if human_llm, require reflection lines in roles section
    meta = META_RE.search(submission_md)
    pair_type = ""
    if meta:
        body = meta.group("body")
        mpt = re.search(r"pair_type:\s*(.+)", body)
        if mpt:
            pair_type = mpt.group(1).strip()

    if "human_llm" in pair_type:
        roles = blocks.get("roles", "")
        # require Kept/Rejected/Why
        missing = []
        for key in ("Kept", "Rejected", "Why"):
            if not re.search(rf"^{key}.*:\s*\S+", roles, re.MULTILINE):
                missing.append(key)
        if missing:
            flags.append(FLAG_MISSING_LLM_REFLECTION)

    # de-dupe while preserving order
    seen = set()
    out_flags = []
    for f in flags:
        if f not in seen:
            seen.add(f)
            out_flags.append(f)
    return out_flags


def build_prompt(rubric: Dict[str, Any], submission_md: str, preflags: List[str]) -> str:
    """
    Tell the model exactly what the rubric is AND exactly what flags are allowed.
    Also: forbid it from judging checkbox "quality" (only "exactly one selected").
    """
    schema = """{
  "score_total": number,
  "criteria": [
    { "criterion_id": string, "points": number, "comment": string }
  ],
  "overall_comment": string,
  "flags": [string]
}"""

    # List criteria
    criteria_lines = []
    for c in rubric["criteria"]:
        criteria_lines.append(
            f'- {c["criterion_id"]} (max {c["max_points"]}): {c["prompt"][:260].strip()}'
        )
    criteria_text = "\n".join(criteria_lines)

    allowed_flags = [
        FLAG_MISSING_SIGNOFF_A,
        FLAG_MISSING_SIGNOFF_B,
        FLAG_MISSING_LLM_REFLECTION,
        FLAG_MISSING_WORK_SUMMARY,
        FLAG_MISSING_SNAG,
        FLAG_MISSING_NEXT_TIME_CHOICE,
    ]

    prompt = f"""
You are grading ONE student submission against a rubric.

STRICT OUTPUT:
- Output ONLY valid JSON (no markdown, no commentary).
- Must match this JSON schema exactly:
{schema}

RUBRIC:
- total_points: {rubric.get("expected_total_points", rubric.get("total_points", 10))}
- criteria:
{criteria_text}

NON-NEGOTIABLE RULES:
- Use only evidence in the submission.
- Each criterion_id must appear exactly once in criteria[].
- points must be between 0 and that criterion's max_points.
- score_total must equal the sum of points.
- Keep comments short, specific, and tied to evidence.
- For "next_time": DO NOT judge the *type* of checkbox chosen. Only require that EXACTLY ONE checkbox is selected and that one-sentence plan exists.

FLAGS:
- flags[] may ONLY contain items from this allowlist:
{json.dumps(allowed_flags, indent=2)}

PRECHECK (deterministic findings):
- If any of these are present, include them in flags[] (unless you verify the submission actually satisfies it):
{json.dumps(preflags, indent=2)}

SUBMISSION (markdown):
{submission_md}
""".strip()

    return prompt


def ollama_generate(
    host: str,
    model: str,
    prompt: str,
    num_predict: int,
    temperature: float,
    timeout_s: int,
) -> str:
    url = host.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
            # stop early if it tries to start formatting
            "stop": ["```", "\n\n\n"],
        },
    }
    r = requests.post(url, json=payload, timeout=timeout_s)
    r.raise_for_status()
    data = r.json()
    resp = data.get("response", "") or ""
    return resp.strip()


def extract_json(text: str) -> Dict[str, Any]:
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        return json.loads(text)

    m = JSON_OBJ_RE.search(text)
    if not m:
        raise ValueError("Model output did not contain a JSON object.")
    return json.loads(m.group(0))


def validate_and_normalize(result: Dict[str, Any], rubric: Dict[str, Any]) -> Dict[str, Any]:
    required_keys = {"score_total", "criteria", "overall_comment", "flags"}
    missing = required_keys - set(result.keys())
    if missing:
        raise ValueError(f"Missing keys in result JSON: {sorted(missing)}")

    if not isinstance(result["criteria"], list):
        raise ValueError("criteria must be a list")

    max_map = {c["criterion_id"]: float(c["max_points"]) for c in rubric["criteria"]}
    order = list(max_map.keys())

    seen = set()
    normalized_criteria = []
    extra_flags: List[str] = []

    for item in result["criteria"]:
        cid = item.get("criterion_id")
        pts = item.get("points")
        comment = item.get("comment", "")

        if cid not in max_map:
            extra_flags.append(f"unknown_criterion_id:{cid}")
            continue
        if cid in seen:
            extra_flags.append(f"duplicate_criterion_id:{cid}")
            continue
        seen.add(cid)

        try:
            pts_f = float(pts)
        except Exception:
            pts_f = 0.0
            extra_flags.append(f"non_numeric_points:{cid}")

        max_pts = max_map[cid]
        if pts_f < 0:
            pts_f = 0.0
        if pts_f > max_pts:
            pts_f = max_pts

        normalized_criteria.append({"criterion_id": cid, "points": pts_f, "comment": str(comment).strip()})

    for cid in max_map.keys():
        if cid not in seen:
            normalized_criteria.append({"criterion_id": cid, "points": 0.0, "comment": "No evidence found."})
            extra_flags.append(f"missing_criterion:{cid}")

    normalized_criteria.sort(key=lambda x: order.index(x["criterion_id"]))
    score_total = sum(c["points"] for c in normalized_criteria)

    combined_flags = list(result.get("flags", []))
    combined_flags += extra_flags
    combined_flags = sorted(set(str(f).strip() for f in combined_flags if str(f).strip()))

    return {
        "score_total": score_total,
        "criteria": normalized_criteria,
        "overall_comment": str(result.get("overall_comment", "")).strip(),
        "flags": combined_flags,
    }


def render_human_text(result: Dict[str, Any], rubric: Dict[str, Any]) -> str:
    total = rubric.get("expected_total_points", rubric.get("total_points", 10))
    lines = [f"Score: {result['score_total']} / {total}", ""]

    max_map = {c["criterion_id"]: c["max_points"] for c in rubric["criteria"]}
    for c in result["criteria"]:
        lines.append(f"- {c['criterion_id']}: {c['points']} / {max_map.get(c['criterion_id'], '?')}")
        if c.get("comment"):
            lines.append(f"  {c['comment']}")
    lines.append("")

    if result.get("overall_comment"):
        lines.append("Overall:")
        lines.append(result["overall_comment"])
        lines.append("")

    if result.get("flags"):
        lines.append("Flags:")
        for f in result["flags"]:
            lines.append(f"- {f}")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rubric", default="03_rubric.json")
    ap.add_argument("--submission", help="Student-filled markdown file")
    ap.add_argument("--init-submission", help="Create a starter submission file at this path and exit")
    ap.add_argument("--template", default="submissions/_TEMPLATE_pp.md", help="Template used for --init-submission")
    ap.add_argument("--model", default="qwen2.5:3b-instruct")
    ap.add_argument("--host", default="http://127.0.0.1:11434")
    ap.add_argument("--out-json", default="04_feedback.json")
    ap.add_argument("--out-txt", default="04_feedback.txt")
    ap.add_argument("--num-predict", type=int, default=650)
    ap.add_argument("--timeout", type=int, default=90)
    args = ap.parse_args()

    if args.init_submission:
        init_submission(args.init_submission, args.template)
        return 0

    if not args.submission:
        raise SystemExit("ERROR: --submission is required (or use --init-submission).")

    rubric = load_rubric(args.rubric)
    submission_md = load_submission(args.submission)

    preflags = precheck_flags(submission_md)
    prompt = build_prompt(rubric, submission_md, preflags)

    # Try once, retry with more tokens if it returns empty
    raw = ollama_generate(args.host, args.model, prompt, num_predict=args.num_predict, temperature=0.0, timeout_s=args.timeout)
    if not raw.strip():
        raw = ollama_generate(args.host, args.model, prompt, num_predict=max(args.num_predict, 900), temperature=0.0, timeout_s=args.timeout)

    result = extract_json(raw)
    normalized = validate_and_normalize(result, rubric)

    Path(args.out_json).write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    Path(args.out_txt).write_text(render_human_text(normalized, rubric), encoding="utf-8")

    print(f"Wrote {args.out_json} and {args.out_txt}")
    print(f"Score_total: {normalized['score_total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


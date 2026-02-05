# Pair Programming Pipeline Contract (Human-Owned)

## Canonical Outputs
- 01_source.md (source of truth)
- 02_canvas.html (Canvas HTML)
- 03_rubric.json (rubric extracted)
- 04_grade.py (local LLM grader)
- 04_feedback.json (machine output)
- 04_feedback.txt (human output)

## Rubric (IDs + Points are sacred; sum must equal 10)
- work_summary: 2
- roles: 4
- snag: 2
- next_time: 2

## Flags (grader must produce flags, not guesses)
- missing_signoff_a
- missing_signoff_b
- missing_llm_reflection
- missing_work_summary
- missing_snag

## LLM Output Schema (must be EXACT)
{
  "score_total": number,
  "criteria": [
    { "criterion_id": string, "points": number, "comment": string }
  ],
  "overall_comment": string,
  "flags": [string]
}

## Parsing Rules
- :::meta block -> metadata dict + checks
- :::criterion{id, points} block -> rubric criterion
- :::signoff -> required checks
- :::private_note -> ignored for scoring


<!--
DOC_KIND: pair_programming_report
DOC_VERSION: 1.2
INTENDED_USE: Canvas_HTML + Rubric_JSON + LLM_Grading
PARSING_NOTES:
- Custom blocks start with ::: and end with :::
- criterion blocks define rubric categories
- Keep ids stable; points must sum to 10
-->

# Pair Programming Report (Team or Solo+LLM) — 10 pts

:::meta
date: 2026-02-04
course: COMSC-1053
section: 1415
pair_type: human_pair

participants:
  - name: Bob R.
    role: Driver
  - name: Alice M.
    role: Navigator

tooling:
  name: ""         # Only if human_llm (ex: ChatGPT, Ollama)
  model: ""        # Only if human_llm (ex: qwen2.5:3b-instruct)
  notes: ""        # Optional (ex: "Used for hints, not full solutions")

task:
  title: "Pair Programming Pipeline: build rubric JSON + grade a filled report"
  artifact: "Repo: swosu/Pair_Programming_Pipeline (local run on faith)"
:::

---

## 1) What you worked on (2 pts)
:::criterion{id="work_summary" points="2"}
- Goal (one line): Generate the rubric JSON and successfully grade a filled pair-programming submission with the local Ollama grader.
- Result (one line): Created submissions/bob_pp01.md, ran 03_build_rubric_json.py to produce 03_rubric.json, then ran 04_grade.py to produce 04_feedback.json + 04_feedback.txt.
:::

---

## 2) Pairing behaviors (4 pts)
:::criterion{id="roles" points="4"}
**Driver (2 concrete actions)**
- D1: Created the submissions/ folder and copied the template into submissions/bob_pp01.md, then filled in every section with concrete evidence.
- D2: Ran the pipeline commands in order (03_build_rubric_json.py then 04_grade.py) and checked the outputs (cat 04_feedback.txt) to verify results.

**Navigator (2 concrete actions)**
- N1: Noticed the template still had blanks and prompted me to add specifics (actual goal/result, real snag/response, and initials).
- N2: Verified rubric alignment by comparing the filled sections to the four criterion IDs (work_summary, roles, snag, next_time) so nothing was missing.

**If human_llm (required):**
- Kept:
- Rejected:
- Why (one line):
:::

---

## 3) One snag + response (2 pts)
:::criterion{id="snag" points="2"}
- Snag (what went wrong / got confusing): 04_grade.py hung waiting for the Ollama response when the prompt got long and I didn’t realize it was still generating.
- Response (what you tried that helped): Reduced the problem to a tiny test case (fill one submission cleanly), re-ran with the correct model running (qwen2.5:3b-instruct), and confirmed Ollama responsiveness with a quick curl test before retrying grading.
:::

---

## 4) Next time (2 pts)
:::criterion{id="next_time" points="2"}
Pick ONE checkbox:
- [ ] Swap roles next time
- [ ] Confirm requirements first
- [X] Test earlier (tiny example)
- [ ] Think out loud more
- [ ] Ask better questions (smaller, sharper)

One sentence: what will you do differently next time?
:::

Next time we will start by grading a single known-good example submission before changing configs or adding automation, so we always have a working baseline.

---

## Sign-off (required)
:::signoff
- Student A initials: BR
- Student B initials (or "LLM"): AM
:::

:::private_note
(Optional) If something needs the instructor’s attention, write it here.
This section can be removed from the shared student copy if desired.
- Note: None.
:::


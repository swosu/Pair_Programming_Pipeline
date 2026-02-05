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
date: YYYY-MM-DD
course: COMSC-____
section: ____
pair_type: human_pair | human_llm

participants:
  - name: Student A
    role: Driver | Navigator
  - name: Student B (or "LLM")
    role: Driver | Navigator

tooling:
  name: ""         # Only if human_llm (ex: ChatGPT, Ollama, Continue)
  model: ""        # Only if human_llm (ex: qwen2.5:3b-instruct)
  notes: ""        # Optional (ex: "Used for hints, not full solutions")

task:
  title: "What did you work on?"
  artifact: ""     # Optional: repo link, file name, screenshot link
:::

---

## 1) What you worked on (2 pts)
:::criterion{id="work_summary" points="2"}
- Goal (one line): 
- Result (one line):   # what exists now that didn’t exist before
:::

---

## 2) Pairing behaviors (4 pts)
:::criterion{id="roles" points="4"}
**Driver (2 concrete actions)**
- D1:
- D2:

**Navigator (2 concrete actions)**
- N1:
- N2:

**If human_llm (required):**
- Kept:     # one helpful thing the model suggested
- Rejected: # one thing you ignored/overruled
- Why (one line):
:::

---

## 3) One snag + response (2 pts)
:::criterion{id="snag" points="2"}
- Snag (what went wrong / got confusing):
- Response (what you tried that helped):
:::

---

## 4) Next time (2 pts)
:::criterion{id="next_time" points="2"}
Pick ONE checkbox:
- [ ] Swap roles next time
- [ ] Confirm requirements first
- [ ] Test earlier (tiny example)
- [ ] Think out loud more
- [ ] Ask better questions (smaller, sharper)

One sentence: what will you do differently next time?
:::

---

## Sign-off (required)
:::signoff
- Student A initials:
- Student B initials (or "LLM"):
:::

:::private_note
(Optional) If something needs the instructor’s attention, write it here.
This section can be removed from the shared student copy if desired.
- Note:
:::


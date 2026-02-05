# Engineering Rules for this Repo (Clean Code-ish)

## Prime Directive
Prefer clarity over cleverness. Code should read like a well-written lab manual.

## General Standards
- Functions should do one thing. Split if you need "and".
- Names are explicit: `md_text`, `html_output`, `parse_meta_block()`. Avoid vague names (`data`, `stuff`, `thing`).
- Keep functions small (target: 5–30 lines).
- Favor pure functions. Minimize global state and side effects.
- No silent failures. Raise errors with helpful messages.
- Every public function gets a docstring: intent + inputs + outputs + exceptions.
- Keep dependencies minimal and pinned.

## Python Specific
- Use type hints for function signatures.
- Use dataclasses for structured data (e.g., parsing metadata from the markdown).
- Logging: prefer `logging` module over print for non-test diagnostics.
- CLI: use `argparse` with `--in`, `--out`, and `--format` flags.

## Testing Standards
- Tests must be deterministic (stable whitespace rules, stable HTML formatting).
- Each test should assert 1 concept.
- Add tests before refactors when possible.

## Output Goals
- HTML output is stable for Canvas.
- Markdown schema is the “source of truth” and must not change without updating:
  - `02_md_to_html.py`
  - tests
  - any future JSON converter

## When using the assistant
- Start with a plan, then implement in small diffs.
- Always update or add tests with code changes.
- If uncertain about intended behavior, ask for examples from `01_source.md`.


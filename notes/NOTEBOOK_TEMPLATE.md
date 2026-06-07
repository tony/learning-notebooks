# Notebook Template Guide

How to create a new study notebook from `notes/notebook_template.py`.

## Steps

1. Copy the template into the right domain + library directory (domains:
   `toolchain/`, `systems/`, `data/`, `ml/`, … — see `notes/taxonomy.md`):

   ```bash
   mkdir -p notebooks/<domain>/<library>; \
   cp notes/notebook_template.py notebooks/<domain>/<library>/NNN_<topic>.py
   ```

   Use the next free number (`001_`, `002_`, …) and a snake_case topic
   (file names must be valid module names — no dashes).

2. Edit the PEP 723 block:
   - Set `dependencies` to what the notebook needs (keep `marimo` in the list).
   - Adjust `requires-python` only if a dependency demands it.
   - Tip: opening with `marimo edit --sandbox` manages this block for you, and
     `uv add --script notebooks/<domain>/<library>/NNN_<topic>.py <package>` works from the CLI.

3. Replace the placeholders:
   - Module docstring: `LIBRARY — TOPIC: summary`.
   - Title cell: what the notebook studies and the questions it answers.
   - Source-reading cell: upstream GitHub URL and the sibling clone path
     (`../<repo>` — see `notes/study_plan.md` for the mapping).

4. Write the study cells. Remember the marimo rules in `AGENTS.md`
   (DAG rule, last expression = output, no magics, cache expensive work).

5. Give every teaching section a markdown heading (`##`, deeper levels as
   needed) — marimo's Outline panel builds its navigation from headings in
   rendered markdown cells. Two rules:
   - Headings must live in *plain* `mo.md` output; anything inside
     `mo.accordion` / `mo.ui.tabs` / `mo.carousel` is excluded from the
     outline.
   - Heading text names the idea (`## Strides and views`), not filler
     (`## Overview`).
   Every `@app.function` / `@app.class_definition` carries a docstring —
   the Documentation panel shows it on hover via jedi.

6. If the notebook is lightweight (no GPU, no model downloads, deps install in
   seconds), add it to the smoke-run list in `.github/workflows/ci.yml`.

## Recipes

Working demonstrations of all of these live in `notebooks/toolchain/marimo/001_basics.py`.

- **Gate expensive work** — `run = mo.ui.run_button(...)` in one cell;
  `mo.stop(not run.value, mo.md("…"))` at the top of the gated cell. Headless
  runs leave the cell gated, which is what makes heavy notebooks CI-safe.
- **Cache by tier** — `@mo.cache` (in-memory) for cheap memoization,
  `@mo.lru_cache(maxsize=…)` when memory-bounded, `with mo.persistent_cache("name"):`
  for model downloads/training (disk, survives restarts, gitignored `__marimo__/`).
- **Reusable + testable code** — move shared imports into a setup cell
  (`with app.setup:`), define single-function cells so they serialize as
  `@app.function` (importable from other modules).
- **Tests inside the notebook** — name a cell `test_<thing>` with only asserts;
  `uv run --with pytest pytest notebooks/<domain>/<library>/NNN_<topic>.py` collects it,
  and CI smoke-runs execute the asserts too.

## Quality Gates

Before committing (gates 2–5 are also one command: `just check`):

1. Headless run exits 0: `uv run notebooks/<domain>/<library>/NNN_<topic>.py`
2. `uv run ruff check .`
3. `uv run ruff format .`
4. `uv run ty check`
5. `uv run marimo check --strict notebooks/ notes/notebook_template.py` and
   `uv run scripts/check_licenses.py`
6. No local paths or PII — must print nothing: `git grep '/home/' -- notebooks/`

(`marimo check --fix` is handy but only point it at `.py` notebooks, with the
notebook's own deps available — see the caution in `AGENTS.md`.)

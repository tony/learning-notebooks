# Notebook Template Guide

How to create a new study notebook from `notes/notebook_template.py`.

## Steps

1. Copy the template into the right library directory:

   ```bash
   mkdir -p notebooks/<library>
   cp notes/notebook_template.py notebooks/<library>/NNN_<topic>.py
   ```

   Use the next free number (`001_`, `002_`, …) and a snake_case topic
   (file names must be valid module names — no dashes).

2. Edit the PEP 723 block:
   - Set `dependencies` to what the notebook needs (keep `marimo` in the list).
   - Adjust `requires-python` only if a dependency demands it.
   - Tip: opening with `marimo edit --sandbox` manages this block for you, and
     `uv add --script notebooks/<library>/NNN_<topic>.py <package>` works from the CLI.

3. Replace the placeholders:
   - Module docstring: `LIBRARY — TOPIC: summary`.
   - Title cell: what the notebook studies and the questions it answers.
   - Source-reading cell: upstream GitHub URL and the sibling clone path
     (`../<repo>` — see `notes/study_plan.md` for the mapping).

4. Write the study cells. Remember the marimo rules in `AGENTS.md`
   (DAG rule, last expression = output, no magics, cache expensive work).

5. If the notebook is lightweight (no GPU, no model downloads, deps install in
   seconds), add it to the smoke-run list in `.github/workflows/ci.yml`.

## Quality Gates

Before committing:

```bash
uv run notebooks/<library>/NNN_<topic>.py   # headless run exits 0
uv run ruff check .
uv run ruff format .
uv run ty check
git grep '/home/' -- notebooks/             # must be empty (no local paths)
```

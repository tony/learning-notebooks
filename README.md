# Learning Notebooks

A study directory for learning Python libraries hands-on through
[marimo](https://github.com/marimo-team/marimo) notebooks — pure-Python,
git-friendly, and each one self-contained.

## Requirements

- [uv](https://github.com/astral-sh/uv) — nothing else. Notebooks bring their
  own dependencies.

## Quick Start

```bash
# Open any notebook in its own isolated environment (zero install)
uvx marimo edit --sandbox notebooks/pandas/001_dataframes.py

# Or, with dev tooling installed:
uv sync
uv run marimo edit --sandbox notebooks/pandas/001_dataframes.py

# Run a notebook headlessly as a script
uv run notebooks/pandas/001_dataframes.py
```

## How It Works

Every notebook is a marimo `.py` file carrying its own dependencies in a
[PEP 723](https://peps.python.org/pep-0723/) inline metadata block:

```python
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "pandas",
# ]
# ///
```

`marimo edit --sandbox` (or plain `uv run`) reads that block and builds an
ephemeral, isolated environment for just that notebook. There is **no shared
runtime environment**: a notebook that needs torch and a notebook that needs
pandas never share a lockfile, and the repo's own `pyproject.toml` only
provides dev tooling (marimo CLI, ruff, ty).

## Layout

- `notebooks/` — the curriculum: one directory per library, numbered
  `NNN_topic.py` notebooks.
- `notes/` — templates and planning: `notebook_template.py`,
  `NOTEBOOK_TEMPLATE.md` (how to author), `study_plan.md` (what to study,
  where the source clones live).

## Create a Notebook

```bash
mkdir -p notebooks/<library>
cp notes/notebook_template.py notebooks/<library>/001_<topic>.py
uv run marimo edit --sandbox notebooks/<library>/001_<topic>.py
```

See `notes/NOTEBOOK_TEMPLATE.md` for authoring rules and quality gates, and
`AGENTS.md` for the marimo-vs-Jupyter gotchas (DAG rule, no magics, caching
expensive cells).

## Development

```bash
uv run ruff check .
uv run ruff format .
uv run ty check
```

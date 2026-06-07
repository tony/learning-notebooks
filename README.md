# Learning Notebooks

A study directory for learning Python libraries hands-on through
[marimo](https://github.com/marimo-team/marimo) notebooks — pure-Python,
git-friendly, and each one self-contained.

## Requirements

- [uv](https://github.com/astral-sh/uv) — nothing else. Notebooks bring their
  own dependencies.

## Quick Start

With [just](https://github.com/casey/just) (recipes are thin wrappers — the
plain commands below always work too):

```bash
just                                            # list all recipes
just list                                       # list notebooks by domain
just edit notebooks/data/polars/001_lazy_frames.py   # editor; prints URL, NO browser
just open notebooks/data/polars/001_lazy_frames.py   # editor + browser
just run  notebooks/data/polars/001_lazy_frames.py   # headless script run
just pick                                       # fuzzy-pick a notebook (fzf)
just new ml statsmodels linear_models           # scaffold from the template
just check                                      # all quality gates
```

Notebook arguments are real paths, so your shell tab-completes them by domain
(`just edit notebooks/data/<TAB>`) with zero setup. Optional recipe-name
completion: `eval "$(just --completions zsh)"` (also bash/fish/powershell/…).

Without just:

```bash
# Open any notebook in its own isolated environment (zero install)
uvx marimo edit --sandbox --headless notebooks/data/pandas/001_dataframes.py

# Or, with dev tooling installed:
uv sync
uv run marimo edit --sandbox notebooks/data/pandas/001_dataframes.py

# Run a notebook headlessly as a script
uv run notebooks/data/pandas/001_dataframes.py
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

- `notebooks/<domain>/<library>/` — the curriculum, grouped by taxonomy domain
  (`toolchain/`, `systems/`, `data/`, `ml/`, …) with one directory per library
  and numbered `NNN_topic.py` notebooks. The cross-corpus index is
  `notes/taxonomy.md`.
- `notes/` — templates and planning: `notebook_template.py`,
  `NOTEBOOK_TEMPLATE.md` (how to author), `study_plan.md` (what to study,
  where the source clones live).

## Create a Notebook

```bash
mkdir -p notebooks/<domain>/<library>
cp notes/notebook_template.py notebooks/<domain>/<library>/001_<topic>.py
uv run marimo edit --sandbox notebooks/<domain>/<library>/001_<topic>.py
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

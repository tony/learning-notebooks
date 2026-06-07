# Learning Notebooks

A study directory for learning Python libraries hands-on through
[marimo](https://github.com/marimo-team/marimo) notebooks — pure-Python,
git-friendly, and each one self-contained.

## Requirements

- [uv](https://github.com/astral-sh/uv) — nothing else. Notebooks bring their
  own dependencies.

## Quick Start

Browse every notebook in marimo's directory gallery — zero install, prints a
URL instead of hijacking your browser:

```bash
uvx marimo edit --headless notebooks/
```

Open a single notebook in its own isolated environment:

```bash
uvx marimo edit --sandbox --headless notebooks/data/pandas/001_dataframes.py
```

Run a notebook headlessly as a script:

```bash
uv run notebooks/data/pandas/001_dataframes.py
```

(With dev tooling installed — `uv sync` — swap `uvx marimo` for `uv run marimo`.)

### Optional: just

[just](https://github.com/casey/just) is an optional convenience — every recipe
is a thin wrapper over the plain commands above. Type `just` by itself to list
the quick commands:

The gallery, as above:

```bash
just gallery
```

Editor — prints the URL, no browser:

```bash
just edit notebooks/data/polars/001_lazy_frames.py
```

Editor + browser:

```bash
just open notebooks/data/polars/001_lazy_frames.py
```

Fuzzy-pick a notebook (fzf):

```bash
just pick
```

Scaffold from the template:

```bash
just new ml statsmodels linear_models
```

All quality gates:

```bash
just check
```

Notebook arguments are real paths, so your shell tab-completes them by domain
(`just edit notebooks/data/<TAB>`) with zero setup. Optional recipe-name
completion: `eval "$(just --completions zsh)"` (also bash/fish/powershell/…).

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

One chained command — scaffold from the template, then open it (or use
`just new <domain> <library> <topic>`):

```bash
mkdir -p notebooks/<domain>/<library>; \
cp notes/notebook_template.py notebooks/<domain>/<library>/001_<topic>.py; \
uv run marimo edit --sandbox notebooks/<domain>/<library>/001_<topic>.py
```

See `notes/NOTEBOOK_TEMPLATE.md` for authoring rules and quality gates, and
`AGENTS.md` for the marimo-vs-Jupyter gotchas (DAG rule, no magics, caching
expensive cells).

## Development

Run the quality gates (or just `just check`):

```bash
uv run ruff check .; \
uv run ruff format .; \
uv run ty check
```

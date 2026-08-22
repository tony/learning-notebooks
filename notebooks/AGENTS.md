# AGENTS.md

Authoring rules and marimo-specific gotchas for the notebooks in this
directory, and for `notes/notebook_template.py`, the template every notebook
is copied from. Read this before creating or editing a notebook. Repo-wide
policy is in the [root AGENTS.md](../AGENTS.md); prose style is in
[.github/WRITING.md](../.github/WRITING.md#notebook-prose-and-output).

## Authoring rules

- **Start every notebook from the template**: copy
  `notes/notebook_template.py`, then edit the PEP 723 block. Follow
  `notes/NOTEBOOK_TEMPLATE.md` for what to change and the quality gates.
- **Every notebook carries a PEP 723 block** at the top with
  `requires-python` and `dependencies`. Opening with `--sandbox` lets
  marimo/uv manage this block automatically (`uv add --script <notebook>
  <package>` also works).
- **One library or concept per notebook.** Numbered files (`001_`, `002_`,
  …) order the study progression within a library directory.
- **Naming**: `notebooks/<domain>/<library>/NNN_snake_case_topic.py` —
  domain directories come from the taxonomy (`toolchain/`, `systems/`,
  `data/`, `ml/`, …), leaf directories are library names (`pandas/`,
  `ibis/`), and every path segment is a valid module name (underscores, no
  dashes).
- **Source-reading cell**: each notebook includes a markdown cell with the
  upstream GitHub URL and, where useful, the in-repo subpath to read
  (`- In the source: \`src/execution/\``). Never author a machine-relative
  clone path (`../../rust-python/polars`) — it leaks a local layout and
  means nothing downstream; where a clone lives locally is resolved at
  runtime (`$STUDY_ROOT` / vcspull), never committed. No absolute home paths
  or PII.
- **Cross-references (opt-in)**: the same source-reading cell may carry a
  `- Concepts:` line of comma-separated slugs and a `- See also:` line of
  backticked `notebooks/…py` paths, parsed like `Upstream:` into the index
  (the `notebook_concept` / `notebook_see_also` / `project_lineage` tables).
  Every concept slug must be registered in a `[[concept]]` block in
  `notes/curriculum.toml` (slug, one-line gloss in our own prose, and the
  projects it appears in), and every see-also must name a real notebook —
  the drift gate fails otherwise. Concept glosses are authored, never lifted
  from the architecture corpus. Untagged notebooks stay valid; this layer is
  grown from the notebooks that use it, not required of all.
- **Plain docstrings, no codes**: the module docstring is human prose — no
  `(Track, Rung)` tag. A notebook's course and rung live in
  `notes/curriculum.toml`: list its path under at least one
  `[[track]].notebooks` entry with a worded `rung`, and ensure its library
  has a `[[project]]`. The drift gate fails on a notebook no track claims or
  a library with no project. Track ids are readable slugs
  (`data/dataframes`), never coded (`B1`).
- **CI-safety**: notebooks with heavy deps (torch, transformers, vllm,
  diffusers, …) or model downloads are *not* added to the CI smoke-run list
  in `.github/workflows/ci.yml`. Only lightweight notebooks go there.

## marimo gotchas (vs Jupyter)

- **DAG rule**: a variable may be defined in only one cell. Prefer
  functional pipelines (`df2 = df.assign(...)`) over re-assignment across
  cells; use underscore-prefixed names (`_tmp`) for cell-local variables.
- **The last expression in a cell is its output** — no `display()` needed.
- **No IPython magics or `!shell`**: use the `timeit` module, `subprocess`,
  `os` instead. `IPython.display` calls are shimmed and mostly work.
- **Expensive work**: gate with `mo.stop(...)` or `mo.ui.run_button()`, and
  wrap model loads in `@mo.persistent_cache` so reactive re-runs don't
  re-download or re-train.
- **Caching tiers**: `@mo.cache` (in-memory, unbounded) →
  `@mo.lru_cache(maxsize=…)` (bounded) → `mo.persistent_cache` (disk,
  survives restarts; writes to gitignored `__marimo__/`).
- **SQL**: `mo.sql()` queries dataframes in scope via DuckDB — prefer it
  when studying ibis/duckdb/sql topics.
- **Widgets**: use `mo.ui.*` (or anywidget); classic ipywidgets are
  second-class. A widget's `.value` never updates in the cell that creates
  it — create in one cell, read in another. Widgets in plain lists/dicts
  don't sync; use `mo.ui.array` / `mo.ui.dictionary` / `.batch()`.
- **Mutations are invisible to the DAG**: mutate an object only in the cell
  that creates it, or derive a new variable. Write idempotent cells.
- **Prefer reactivity over `mo.state`/`on_change` handlers** — referencing a
  widget's `.value` in another cell is almost always enough; `mo.state` is
  only for deliberate cycles.
- **Outline panel reads markdown headings** (h1–h6) from rendered md cells —
  give every teaching section a `##` heading so notebooks are navigable.
  Headings inside `mo.accordion`/`mo.ui.tabs`/`mo.carousel` are excluded
  from the outline; keep them in plain md cells. The Documentation panel
  shows docstrings on hover (jedi) — every `@app.function` and
  `@app.class_definition` carries one.

## marimo power features

- **Setup cell** (`with app.setup:`): runs before all cells; its symbols
  are usable everywhere without appearing in cell signatures — required for
  `@app.function`.
- **Top-level functions** (`@app.function`, `@app.class_definition`): cells
  with a single def/class referencing only setup-cell symbols serialize
  top-level — importable from other modules and visible to plain pytest.
- **Tests in notebooks**: cells named `test_*` (or containing only test
  code) are pytest-discoverable:
  `uv run --with pytest pytest notebooks/<lib>/<notebook>.py`. They also
  assert during CI smoke-runs.
- **Modes**: `mo.app_meta().mode` reports `edit`/`run`/`script`/`test` —
  branch on it for CI-safe notebooks. `mo.cli_args()` / `mo.query_params()`
  parameterize runs.
- **Exemplar**: `notebooks/toolchain/marimo/001_basics.py` demonstrates all
  of the above, stdlib-only.

## Quality gates before committing a notebook

The repo-wide gates in [CONTRIBUTING.md](../.github/CONTRIBUTING.md#the-gates)
apply. Before committing a notebook specifically:

1. `uv run <notebook>.py` exits 0 (headless script run).
2. `uv run marimo check --strict notebooks/ notes/notebook_template.py`
   passes. Caution with `--fix`: run it only on `.py` notebooks, and only
   when the notebook's own dependencies are available — without them it
   cannot parse `mo.sql()` strings and strips real dependency edges.
3. No absolute local paths or PII in the file:
   `git grep '/home/' -- notebooks/` stays empty.
4. `uv run scripts/curriculum.py check` passes — regenerate with
   `just sync` after editing notebook metadata or
   `notes/curriculum.toml`, and commit the result alongside the change.

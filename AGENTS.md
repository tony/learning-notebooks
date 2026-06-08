# AGENTS.md

This file provides guidance to coding agents (and humans) working in this repository.

## What This Repo Is

A study directory of [marimo](https://github.com/marimo-team/marimo) notebooks for learning
Python libraries hands-on. Each notebook is a self-contained, pure-Python file that carries its
own dependencies via [PEP 723](https://peps.python.org/pep-0723/) inline script metadata and runs
in an isolated, ephemeral [uv](https://github.com/astral-sh/uv) environment (`--sandbox`).

There is **no shared runtime environment**: the repo's `pyproject.toml` only provides dev tooling
(marimo CLI, ruff, type checker). A torch notebook and a pandas notebook never share a lockfile.

## Development Commands

The user-facing command tour (gallery, just recipes, completions) lives in
`README.md`; bare `just` lists the optional recipe wrappers. Below is the
agent dev loop.

### Essential Commands

Install dev tooling (marimo CLI, ruff, type checker):

```bash
uv sync
```

Open a notebook in the editor, in its own isolated env (`uvx marimo` works the
same way with zero install):

```bash
uv run marimo edit --sandbox notebooks/data/pandas/001_dataframes.py
```

Run a notebook headlessly as a script (uv resolves its PEP 723 deps):

```bash
uv run notebooks/data/pandas/001_dataframes.py
```

Create a new notebook from the template and open it:

```bash
cp notes/notebook_template.py notebooks/<domain>/<library>/001_<topic>.py; \
uv run marimo edit --sandbox notebooks/<domain>/<library>/001_<topic>.py
```

Lint, format, and type check:

```bash
uv run ruff check .; \
uv run ruff format .; \
uv run ty check
```

marimo's notebook-aware linter — scoped to `.py` notebooks, because
`marimo check` treats prose `.md` files as markdown notebooks and must not
touch them:

```bash
uv run marimo check --strict notebooks/ notes/notebook_template.py
```

## Project Structure

- `notebooks/<domain>/<library>/`: the curriculum — taxonomy-domain directories
  (`toolchain/`, `systems/`, `data/`, `ml/`; later `ai_tuning/`, `ai_serving/`,
  `enterprise/` as their first notebooks land), each holding one directory per library with
  numbered `NNN_topic.py` marimo notebooks. All study content lives here. Notebooks for **any**
  taxonomy domain are born in this repo; a track graduates to a `learning-<track>` sibling repo
  only if it outgrows this one (the index is `notes/taxonomy.md`).
- `notes/`: templates, planning, and the curriculum manifest. `notebook_template.py`,
  `NOTEBOOK_TEMPLATE.md`, `study_plan.md`, and `curriculum.toml` (the authored overlay:
  the `[ladder]` rungs, `[[track]]` courses with per-notebook rung, and the `[[project]]`
  registry that joins each studied library to its upstream + tracks) are hand-edited;
  `taxonomy.md`, `catalog.jsonl`, and `coverage.md` are **generated** from the manifest +
  notebooks by `scripts/curriculum.py` — edit the sources, then `just sync`. `sources.jsonl`
  is a **third provenance tier**: the portable source map, built locally from the architecture
  studies (`just sources`) and committed as version-pinned GitHub URLs. It is corpus-derived
  but never CI-regenerated — the architecture corpus is a *research input*, not a runtime
  dependency — so `check` validates the committed file's **shape** (portable blob URLs, known
  projects, no local paths), never its freshness; do **not** add it to the `render()` drift set.
  The narrative around the table is authored in `taxonomy.head.md` / `taxonomy.foot.md`.
  **Not** study content — do not put notebooks here.
- `.github/workflows/ci.yml`: lint, format, type check, and headless smoke-runs of light
  notebooks.

## Authoring Rules

- **Start every notebook from the template**: copy `notes/notebook_template.py`, then edit the
  PEP 723 block. Follow `notes/NOTEBOOK_TEMPLATE.md` for what to change and quality gates.
- **Every notebook must carry a PEP 723 block** at the top with `requires-python` and
  `dependencies`. Opening with `--sandbox` lets marimo/uv manage this block automatically
  (`uv add --script <notebook> <package>` also works).
- **One library/concept per notebook.** Numbered files (`001_`, `002_`, …) order the study
  progression within a library directory.
- **Naming**: `notebooks/<domain>/<library>/NNN_snake_case_topic.py` — domain dirs come from
  the taxonomy (`toolchain/`, `systems/`, `data/`, `ml/`, …), leaf directories are library
  names (`pandas/`, `ibis/`), and every path segment is a valid module name (underscores,
  no dashes).
- **Source-reading cell**: each notebook includes a markdown cell with the **upstream GitHub
  URL** and, where useful, the in-repo subpath to read (`- In the source: \`src/execution/\``).
  Never author a machine-relative clone path (`../../rust-python/polars`) — it leaks a local
  layout and means nothing downstream; where a clone lives locally is resolved at runtime
  (`$STUDY_ROOT` / vcspull), never committed. No absolute home paths or PII.
- **Cross-references (opt-in)**: the same source-reading cell may carry a `- Concepts:` line of
  comma-separated slugs and a `- See also:` line of backticked `notebooks/…py` paths, parsed
  like `Upstream:` into the index (the `notebook_concept` / `notebook_see_also` / `project_lineage`
  tables). Every concept slug must be registered in a `[[concept]]` block in `notes/curriculum.toml`
  (slug + one-line gloss in our own prose + the projects it appears in) and every see-also must name
  a real notebook — the drift gate fails otherwise. Concept glosses are authored, never lifted from
  the architecture corpus. Untagged notebooks stay valid; this layer is grown from the notebooks
  that use it, not required of all.
- **Plain docstrings, no codes**: the module docstring is human prose — **no `(Track, Rung)`
  tag**. A notebook's course and rung live in `notes/curriculum.toml`: list its path under at
  least one `[[track]].notebooks` entry with a worded `rung`, and ensure its library has a
  `[[project]]`. The drift gate fails on a notebook no track claims or a library with no
  project. Track ids are readable slugs (`data/dataframes`), never coded (`B1`).
- **CI-safety**: notebooks with heavy deps (torch, transformers, vllm, diffusers, …) or model
  downloads are *not* added to the CI smoke-run list in `.github/workflows/ci.yml`. Only
  lightweight notebooks go there.
- **Doc style — code blocks are paste-and-run units**: one command per triple-backtick block,
  so pasting a block runs exactly one intended action. Don't blur multiple commands annotated
  by comments into the same block — explanations belong in prose above it. A multi-step
  sequence may share a block only when explicitly chained with `;` / `; \` (the chain *is*
  the single action). Command menus are per-command blocks with prose lead-ins, not tables.

## marimo Gotchas (vs Jupyter)

- **DAG rule**: a variable may be defined in only one cell. Prefer functional pipelines
  (`df2 = df.assign(...)`) over re-assignment across cells; use underscore-prefixed names
  (`_tmp`) for cell-local variables.
- **The last expression in a cell is its output** — no `display()` needed.
- **No IPython magics or `!shell`**: use the `timeit` module, `subprocess`, `os` instead.
  `IPython.display` calls are shimmed and mostly work.
- **Expensive work**: gate with `mo.stop(...)` or `mo.ui.run_button()`, and wrap model loads in
  `@mo.persistent_cache` so reactive re-runs don't re-download/re-train.
- **Caching tiers**: `@mo.cache` (in-memory, unbounded) → `@mo.lru_cache(maxsize=…)` (bounded) →
  `mo.persistent_cache` (disk, survives restarts; writes to gitignored `__marimo__/`).
- **SQL**: `mo.sql()` queries dataframes in scope via DuckDB — prefer it when studying
  ibis/duckdb/sql topics.
- **Widgets**: use `mo.ui.*` (or anywidget); classic ipywidgets are second-class. A widget's
  `.value` never updates in the cell that creates it — create in one cell, read in another.
  Widgets in plain lists/dicts don't sync; use `mo.ui.array` / `mo.ui.dictionary` / `.batch()`.
- **Mutations are invisible to the DAG**: mutate an object only in the cell that creates it,
  or derive a new variable. Write idempotent cells.
- **Prefer reactivity over `mo.state`/`on_change` handlers** — referencing a widget's `.value`
  in another cell is almost always enough; `mo.state` is only for deliberate cycles.
- **Outline panel reads markdown headings** (h1–h6) from rendered md cells — give every
  teaching section a `##` heading so notebooks are navigable. Headings inside
  `mo.accordion`/`mo.ui.tabs`/`mo.carousel` are excluded from the outline; keep them in plain
  md cells. The Documentation panel shows docstrings on hover (jedi) — every `@app.function`
  and `@app.class_definition` carries one.

## marimo Power Features

- **Setup cell** (`with app.setup:`): runs before all cells; its symbols are usable everywhere
  without appearing in cell signatures — required for `@app.function`.
- **Top-level functions** (`@app.function`, `@app.class_definition`): cells with a single
  def/class referencing only setup-cell symbols serialize top-level — importable from other
  modules and visible to plain pytest.
- **Tests in notebooks**: cells named `test_*` (or containing only test code) are pytest-
  discoverable: `uv run --with pytest pytest notebooks/<lib>/<notebook>.py`. They also assert
  during CI smoke-runs.
- **Modes**: `mo.app_meta().mode` reports `edit`/`run`/`script`/`test` — branch on it for
  CI-safe notebooks. `mo.cli_args()` / `mo.query_params()` parameterize runs.
- **Exemplar**: `notebooks/toolchain/marimo/001_basics.py` demonstrates all of the above, stdlib-only.

## Quality Gates (before committing a notebook)

1. `uv run <notebook>.py` exits 0 (headless script run).
2. `uv run ruff check .` and `uv run ruff format .` pass.
3. Type check passes (`uv run ty check`).
4. `uv run marimo check --strict notebooks/ notes/notebook_template.py` passes. Caution with
   `--fix`: run it only on `.py` notebooks, and only when the notebook's own deps are available —
   without them it can't parse `mo.sql()` strings and strips real dependency edges.
5. No absolute local paths or PII in the file (`git grep '/home/'` should stay empty).
6. `uv run scripts/curriculum.py check` passes — `notes/taxonomy.md` is generated, so after
   editing notebook metadata or `notes/curriculum.toml`, regenerate with `just sync` and
   commit the result alongside the change.

## Git Commit Standards

Format commit messages as:

```
Scope(type[detail]): concise description

why: Explanation of necessity or impact.

what:
- Specific technical changes made
- Focused on a single topic
```

The blank line between the `why:` block and the `what:` block is
optional — useful when the `why:` body runs to multiple lines and the
two sections benefit from visual separation.

Common commit types:

- **feat**: New features or enhancements
- **fix**: Bug fixes
- **refactor**: Code restructuring without functional change
- **docs**: Documentation updates
- **chore**: Maintenance (dependencies, tooling, config)
- **test**: Test-related updates
- **style**: Code style and formatting
- **py(deps)**: Dependencies
- **py(deps[dev])**: Dev Dependencies
- **ai(rules[AGENTS])**: AI rule updates
- **ai(claude[rules])**: Claude Code rules (CLAUDE.md)

Subjects are plain English. Never put taxonomy codes (A1, C3, L2) or other
repo-internal shorthand in the subject line — a reader of `git log --oneline`
should understand every title cold. Taxonomy references belong in the body,
spelled out (e.g. "fills the languages-and-runtimes row in notes/taxonomy.md").

Example:

```
polars(feat[lazy]): Inspect query plans before collecting

why: Show the optimizer's predicate pushdown so readers stop guessing
what .explain() output means.

what:
- Add notebooks/data/polars/001_lazy_frames.py from the template
- Register the notebook in the CI smoke-run list
- Link the notebook from its taxonomy row
```

For multi-line commits, use heredoc to preserve formatting:

```bash
git commit -m "$(cat <<'EOF'
Scope(type[detail]): concise description

why: Explanation of the change.

what:
- First change
- Second change
EOF
)"
```

## AI Slop Prevention

Treat AI slop as **review-hostile noise**, not as proof that text or
code is wrong. The goal is to maximize information density by removing
artifacts that make the repository harder to trust or navigate.

### The Anti-Slop Rubric

Before committing, audit all AI-assisted changes for these noise
patterns:

- **AI Signatures:** Remove "Generated by", footers, conversational
  filler ("Certainly!", "Here is..."), unexplained emojis (🤖, ✨), and
  AI-tool metadata.
- **Brittle References:** Avoid hard-coded line numbers, fragile
  file/test counts, dated "as of" claims, bare SHAs, and local
  absolute paths unless they are strict evidentiary artifacts (e.g.,
  benchmark logs).
- **Diff Narration:** Do not restate what moved, was renamed, or was
  removed in artifacts the downstream reader holds: code, docstrings,
  README, CHANGES, PR descriptions, or release notes. The diff and
  commit message already carry this history.
- **Branch-Internal Narrative:** Do not mention intermediate branch
  states, abandoned approaches, or "no longer" behavior unless users
  of a published release actually experienced the old state (**The
  Published-Release Test**).
- **Low-Value Scaffolding:** Remove ownerless TODOs (`TODO: revisit`),
  unused future-proofing, debug artifacts, and defensive wrappers that
  do not protect a currently reachable failure mode.
- **Prose Inflation:** Replace generic AI "tells" like *comprehensive,
  robust, seamless, production-ready, leverage, delve, tapestry,* and
  *best practices* with concrete descriptions of behavior,
  constraints, or trade-offs.

### Preservation & Context

**When unsure, leave the text in place and ask.** Subjective cleanup
must never be a reason to remove load-bearing rationale.

- **Preserve the "Why":** You MUST NOT delete comments that document
  invariants, protocol constraints, platform quirks, security
  boundaries, and upstream workarounds.
- **Evidence is Immune:** Preserve exact counts, dates, and SHAs when
  they serve as evidence in benchmark results, release notes, stack
  traces, or lockfiles.
- **Behavior Over Inventory:** A useful description explains what
  changed for the *system or user*; it does not provide an inventory
  of files or functions the diff already shows.

### The Published-Release Test

Long-running branches accumulate tactical decisions — renames,
refactors, attempts-then-reverts. When deciding what counts as
branch-internal, use trunk or the parent branch as the baseline — not
intermediate states inside the current branch. Ask:

> Did users of the most recently published release ever experience
> this old name, old behavior, or bug?

If the answer is **no**, it is branch-internal narrative. Move it to
the commit message and describe only the final state in the artifact.

**Keep in shipped artifacts:**

- Deprecations and migration guides for symbols that actually shipped.
- `### Fixes` entries for bugs that affected users of a published
  release.
- Comments explaining *why the current code looks this way*
  (invariants, platform quirks) that make sense to a reader who never
  saw the previous version.

### Cleanup in Hindsight

When applying these rules retroactively from inside a feature branch,
first establish scope by diffing against the parent branch (or trunk)
to identify which commits this branch actually introduced. Then:

- **In-branch commits:** Prompt the user with two options: `fixup!`
  commits with `git rebase --autosquash` to address each causal commit
  at its source, or a single cleanup commit at branch tip.
- **Trunk/Parent commits:** Default to leaving them alone. Act only on
  explicit user instruction. If the user opts in, fold the cleanup
  into a single commit at branch tip; do not rewrite shared history.
- **Scope guard:** If cleaning prior slop would touch a colleague's
  work or expand the branch beyond its stated goal, stay in lane:
  protect the current goal and leave prior slop alone.

# AGENTS.md

A study directory of [marimo](https://github.com/marimo-team/marimo)
notebooks for learning Python libraries hands-on. Each notebook is a
self-contained, pure-Python file that carries its own dependencies via
[PEP 723](https://peps.python.org/pep-0723/) inline script metadata and runs
in an isolated, ephemeral [uv](https://github.com/astral-sh/uv) environment
(`--sandbox`). There is no shared runtime environment: the root
`pyproject.toml` provides only dev tooling (marimo, ruff, ty) — a torch
notebook and a pandas notebook never share a lockfile.

Follow the conventions already in the tree, and keep a change scoped to
what was asked for.

## What is here

| Path | What it is |
| ---- | ---------- |
| `notebooks/<domain>/<library>/` | The curriculum: numbered `NNN_topic.py` marimo notebooks, one directory per library. See [notebooks/AGENTS.md](notebooks/AGENTS.md). |
| `notes/curriculum.toml` | Authored overlay: tracks, rungs, the project registry, concepts. Not study content — notebooks go under `notebooks/`. |
| `notes/taxonomy.head.md`, `notes/taxonomy.foot.md` | Hand-authored narrative wrapped around the generated taxonomy table. |
| `notes/taxonomy.md`, `notes/catalog.jsonl`, `notes/coverage.md` | Generated from `curriculum.toml`, the notebooks, and the head/foot narrative by `scripts/curriculum.py` — never hand-edit. |
| `notes/sources.jsonl` | Portable, version-pinned source-URL map; committed, never CI-regenerated. |
| `notes/notebook_template.py`, `notes/NOTEBOOK_TEMPLATE.md` | The notebook template and its authoring guide. |
| `scripts/curriculum.py` | Render/check/query/find engine for the curriculum index. |
| `scripts/check_licenses.py` | License deny-list gate over notebook PEP 723 dependencies. |
| `tests/` | Unit tests for `scripts/curriculum.py` (stdlib-only). |
| `.github/workflows/ci.yml` | Lint, format, type check, `marimo check`, license and drift gates, unit tests, notebook smoke-runs. |

Notebooks for any taxonomy domain are born here; a track graduates to a
`learning-<track>` sibling repo only if it outgrows this one.

## Which policy applies

- Documentation, user-facing text, commit messages, docstrings, and source
  comments: [.github/WRITING.md](.github/WRITING.md)
- Environment, the gates, tests, and pull requests:
  [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md)
- marimo authoring rules and gotchas:
  [notebooks/AGENTS.md](notebooks/AGENTS.md)

Each of those is the single home for its subject. Where a rule seems to be
stated twice, the file listed above is the one that governs.

## Change discipline

- Make the smallest coherent change that solves the verified problem; keep
  unrelated cleanup out of it.
- Reuse an existing file, helper, API, or test before adding a new one.
- Add a file only for a durable boundary — a distinct responsibility,
  independent reuse, or splitting an oversized module — not for a
  single-use helper or a one-line re-export.
- Add a test for every behaviour change to `scripts/curriculum.py`; register
  every added, moved, or reclassified notebook in `notes/curriculum.toml`.
- A passing gate is evidence only once it has been shown capable of
  failing. Pair a new test with a deliberate break that proves it bites.

`notes/taxonomy.md`, `notes/catalog.jsonl`, and `notes/coverage.md` are
generated, not authored — edit `notes/curriculum.toml` or the notebooks,
then `just sync`, and commit the regenerated files together.
`notes/sources.jsonl` is the exception: hand-committed, corpus-derived, and
never CI-regenerated.

## References

- [notes/taxonomy.md](notes/taxonomy.md) — the curriculum index.
- [notes/study_plan.md](notes/study_plan.md) — what to study next.
- [marimo](https://github.com/marimo-team/marimo),
  [uv](https://github.com/astral-sh/uv) — the two tools every notebook
  depends on.

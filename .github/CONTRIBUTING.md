# Contributing

Thanks for looking. The most useful thing right now is a bug report with a
reproduction — a gate that fails locally but passes in CI (or the reverse),
a notebook that will not run headless, or a curriculum-drift error you
cannot explain — or a note on where a notebook's upstream link or claim has
gone stale.

How this project writes prose — README, notebook prose, commit messages,
docstrings, and source comments — is set out separately in
[WRITING.md](WRITING.md). Read that before changing any of it. The
constraints every change is held to, and the map of what is where, are in
[AGENTS.md](../AGENTS.md).

## Getting set up

```console
$ uv sync
```

This installs dev tooling only — marimo's CLI, ruff, and ty. There are no
runtime dependencies to sync: every notebook resolves its own via PEP 723
inline script metadata (see [AGENTS.md](../AGENTS.md)).

## The gates

CI (`.github/workflows/ci.yml`) is the order of record; every gate it runs
has to pass before a change is done.

Lint:

```console
$ uv run ruff check .
```

Format check:

```console
$ uv run ruff format --check .
```

Type-check `notes/` and `scripts/`:

```console
$ uv run ty check notes scripts
```

Type-check notebooks. `ty` ignores `[tool.ty]` configuration for PEP 723
scripts, so these ignores are passed on the command line instead of in
`pyproject.toml`:

```console
$ uv run ty check notebooks \
    --ignore unresolved-import \
    --ignore unresolved-attribute
```

marimo's notebook-aware linter, scoped to `.py` notebooks — `marimo check`
treats a prose `.md` file as a markdown notebook and must not touch one:

```console
$ uv run marimo check --strict notebooks/ notes/notebook_template.py
```

License deny-list over every notebook's PEP 723 dependencies (GPL / AGPL /
SSPL / BUSL / RSAL families; MPL-2.0 is a warning, acceptable only as a
dev/test dependency):

```console
$ uv run scripts/check_licenses.py
```

Curriculum drift — fails when a generated file in `notes/` is stale, a
`notes/curriculum.toml` path no longer exists, or a notebook is unclaimed by
every track:

```console
$ uv run scripts/curriculum.py check
```

Unit tests for the curriculum engine:

```console
$ uv run --with pytest pytest tests/
```

`pytest` is not a project dependency, so `uv sync` does not install it —
`--with pytest` pulls it in for this invocation only. This repository
collects no doctests, so there is no separate documentation gate; see
[Documented examples that run](WRITING.md#documented-examples-that-run) for
what that means in practice.

`just check` runs most of these gates as one command, with two gaps worth
knowing: its `ty check` step calls `ty` with no path or ignore flags, unlike
the two scoped invocations above, and it does not run CI's notebook
smoke-run step at all. Treat the commands in this section, which match CI,
as authoritative.

Before claiming a test or a gate works, show it failing. A gate that has
never been red is an assumption.

## Tests

`tests/` holds unit tests for `scripts/curriculum.py` only. The curriculum
engine is stdlib-only, so the suite needs no notebook sandbox, no marimo
runtime, and no network access. `tests/conftest.py` adds `scripts/` to
`sys.path` so the tests can `import curriculum` directly — there is no
package install step.

A notebook's own correctness is checked differently, not by this suite: a
headless run (`uv run <notebook>.py`), `marimo check --strict`, and, for
lightweight notebooks, the CI smoke-run step. A notebook may also carry
`test_*` cells, which pytest collects
(`uv run --with pytest pytest <notebook>.py`) and which assert during a
headless run too.

## Documentation

There is no Sphinx or MkDocs build. "Documentation" here means the
generated files under `notes/`: `notes/taxonomy.md`, `notes/catalog.jsonl`,
and `notes/coverage.md` are rendered from `notes/curriculum.toml`, the
notebooks, and the hand-authored narrative in `notes/taxonomy.head.md` /
`notes/taxonomy.foot.md` by `scripts/curriculum.py`. Never hand-edit the
generated files themselves — edit `curriculum.toml`, a notebook, or the
head/foot narrative instead. After changing any of those:

```console
$ just sync
```

Commit the regenerated files alongside the change; the curriculum-drift gate
fails otherwise.

`notes/sources.jsonl` is different: a portable, version-pinned source-URL
map built locally from architecture studies, not from this repository's own
state. Rebuild it when the studies change:

```console
$ just sources
```

CI validates only its shape — portable blob URLs, known projects, no local
paths — never its freshness, so a stale entry does not fail the build. It
is deliberately excluded from the drift check's own render-and-compare loop
(`scripts/curriculum.py`'s `render()`); keep it that way when touching that
function, since re-including it would make an unrelated code change fail
the gate on a stale research artefact.

## Pull requests

One subject per pull request. Unrelated cleanup found along the way belongs
in its own commit, and usually in its own pull request.

Discuss a substantial change via an issue before making it.

Commit format is in [WRITING.md](WRITING.md#commits).

## Decorum

- Participants will be tolerant of opposing views.
- Participants must ensure that their language and actions are free of
  personal attacks and disparaging personal remarks.
- When interpreting the words and actions of others, participants should
  always assume good intentions.
- Behaviour which can be reasonably considered harassment will not be
  tolerated.

Based on
[Ruby's Community Conduct Guideline](https://www.ruby-lang.org/en/conduct/).

## Security

Please do not open a public issue for a vulnerability. There is no
`SECURITY.md` in this repository; contact the maintainer through GitHub
directly.

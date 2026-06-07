# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""curriculum — the index notebook: FTS5 search and rollups over this repo's catalog."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="curriculum: the index notebook")

with app.setup:
    import sqlite3
    import sys
    from pathlib import Path

    import marimo as mo

    # The engine lives in scripts/curriculum.py — import it as a module so the
    # notebook and the CLI share one parser (no second source of truth).
    # __file__ anchors script runs (where the marimo context isn't up yet);
    # inside the marimo runtime cells have no __file__, so fall back to
    # mo.notebook_dir().
    try:
        _nb_dir = Path(__file__).resolve().parent
    except NameError:
        _nb_dir = mo.notebook_dir()
    sys.path.insert(0, str(_nb_dir.parent.parent.parent / "scripts"))

    import curriculum


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # curriculum: the index notebook

    This repo's knowledge layer is **derived**: notebooks own their mechanical
    metadata, `notes/curriculum.toml` owns the editorial overlay, and
    `notes/taxonomy.md` is generated from both. This notebook is the
    interactive surface over that catalog — the same SQLite/FTS5 ideas the
    eval-harness series teaches, pointed at the repo's own corpus.

    Everything below rebuilds from sources on each run. Nothing here can go
    stale, because nothing here is stored. One honest limit: the index sees
    *authored* code and markdown only — marimo `.py` files never contain
    runtime outputs, so results and metrics are not searchable.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://www.sqlite.org/fts5.html>
    - In the source: `ext/fts5/` (the tokenizer, bm25, and snippet machinery
      this notebook drives)
    - The engine under this UI: `scripts/curriculum.py` (parser, renderer,
      index builder) over `notes/curriculum.toml` (the authored overlay).
    - Sibling labs: `../learning-ai-tuning/notebooks/eval/` builds the same
      FTS5 + BM25 stack from first principles (the eval-harness track in `notes/taxonomy.md`).
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## The catalog

    One merged record per notebook (Grain A joined to its claiming tracks).
    Sort and filter live — this is `notes/catalog.jsonl` before it hits disk.
    """)
    return


@app.cell
def _():
    nbs, tracks = curriculum.index()
    return nbs, tracks


@app.cell
def _(nbs, tracks):
    _claimed = curriculum.claims(tracks)
    catalog_rows = [
        {
            "path": _nb.path,
            "track": _nb.track,
            "rung": _nb.rung,
            "tracks": ", ".join(_t.id for _t in _claimed.get(_nb.path, [])),
            "title": _nb.title,
            "tests": "yes" if _nb.has_tests else "-",
        }
        for _nb in nbs
    ]
    mo.ui.table(catalog_rows, page_size=12, label=f"{len(catalog_rows)} notebooks")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Search

    FTS5 `MATCH` with porter stemming and bm25 ranking — `batching` finds
    "batch", and results are ordered by relevance, two things `rg` cannot do.
    For literal text, `rg` stays the faster tool.
    """)
    return


@app.cell
def _():
    search = mo.ui.text(
        placeholder="bm25, zero copy, batching, Little's law ...", label="FTS5 query"
    )
    search
    return (search,)


@app.cell
def _():
    conn = curriculum.build_db()
    return (conn,)


@app.cell
def _(conn, search):
    mo.stop(not search.value, mo.md("*Type a query above — try `bm25` or `zero copy`.*"))
    try:
        _rows = conn.execute(
            "SELECT path, bm25(notebook_fts) AS score,"
            " snippet(notebook_fts, 1, '**', '**', '...', 12)"
            " FROM notebook_fts WHERE notebook_fts MATCH ?"
            " ORDER BY bm25(notebook_fts)",
            (search.value,),
        ).fetchall()
        _hits = [
            f"- `{_path}` (bm25 {_score:.2f})\n\n    {' '.join(_snippet.split())}"
            for _path, _score, _snippet in _rows
        ]
        _body = (
            "\n".join(_hits) if _hits else "*No FTS matches — `rg` may still find literal text.*"
        )
    except sqlite3.OperationalError as _err:
        _body = f'*FTS5 could not parse that query ({_err}) — try plain words or `"a phrase"`.*'
    mo.md(_body)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Coverage

    The same rollups `notes/coverage.md` commits, computed live.
    """)
    return


@app.cell
def _(nbs, tracks):
    mo.hstack(
        [
            mo.stat(value=str(len(nbs)), label="notebooks"),
            mo.stat(value=str(len(tracks)), label="tracks"),
            mo.stat(
                value=str(sum(1 for _nb in nbs if _nb.rung is not None)),
                label="with a rung",
            ),
            mo.stat(
                value=str(sum(1 for _nb in nbs if _nb.has_tests)),
                label="with test cells",
            ),
        ],
        justify="start",
        gap=2,
    )
    return


@app.cell
def _(nbs):
    _tree: dict[str, dict[str, list[str]]] = {}
    for _nb in nbs:
        _tree.setdefault(_nb.domain, {}).setdefault(_nb.library, []).append(
            f"{_nb.path.rsplit('/', 1)[-1]} ({_nb.rung or 'no rung'})"
        )
    mo.tree(_tree)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Drift

    What CI's `Curriculum drift` step checks, evaluated here: are the
    committed renders current, and does every notebook belong to a track?
    """)
    return


@app.cell
def _(nbs, tracks):
    _stale = [
        str(_path.relative_to(curriculum.REPO_ROOT))
        for _path, _content in curriculum.render(write=False).items()
        if not _path.exists() or _path.read_text(encoding="utf-8") != _content
    ]
    _unclaimed = [_nb.path for _nb in nbs if _nb.path not in curriculum.claims(tracks)]
    _problems = [f"stale render: `{_p}`" for _p in _stale]
    _problems += [f"unclaimed notebook: `{_p}`" for _p in _unclaimed]
    if _problems:
        _msg = mo.callout(
            mo.md("Drift found — run `just sync`:\n\n" + "\n".join(f"- {_p}" for _p in _problems)),
            kind="warn",
        )
    else:
        _msg = mo.callout(
            mo.md("No drift: renders are current and every notebook is claimed by a track."),
            kind="success",
        )
    _msg
    return


@app.cell
def test_every_notebook_is_claimed():
    _nbs, _tracks = curriculum.index()
    _claimed = curriculum.claims(_tracks)
    for _nb in _nbs:
        assert _nb.path in _claimed, f"unclaimed: {_nb.path}"
    return


@app.cell
def test_fts_ranks_the_faiss_notebook_for_bm25():
    _conn = curriculum.build_db()
    _paths = [
        _row[0]
        for _row in _conn.execute("SELECT path FROM notebook_fts WHERE notebook_fts MATCH 'bm25'")
    ]
    assert any("faiss" in _p for _p in _paths), _paths
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    The catalog is queryable from three surfaces now: `rg`/`jq` in the shell,
    `just q`/`just find` over this same index, and this notebook. The eval-harness
    series goes deeper on every piece (external-content FTS tables, BM25 from
    scratch, tantivy).

    TODO(you): add a `## Stale plans` panel — join `notes/study_plan.md`
    paths against the catalog and flag rows whose notebook already exists
    with status `existing`.
    """)
    return


if __name__ == "__main__":
    app.run()

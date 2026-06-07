# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "sortedcontainers",
# ]
# ///

"""sortedcontainers — ordered structures: sorted views without trees."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="sortedcontainers: ordered structures")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # sortedcontainers: ordered structures

    Seed notebook (taxonomy A2). Pure-Python sorted collections that beat
    C-implemented trees in practice — built on a **list of sublists** plus a
    maintained index, not a balanced tree.

    This seed only *samples* the API; the data-structures curriculum proper
    lives in `../learning-dsa/notes/progression-ds.md` (and
    `progression-algo.md` for the algorithms) — go there for the real study.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/grantjenks/python-sortedcontainers>
    - Implementation notes worth reading first:
      <https://grantjenks.com/docs/sortedcontainers/implementation.html>
    - Companion curriculum: `../learning-dsa/notes/` (BST/AVL progressions show
      what this library deliberately avoids).
    """)
    return


@app.cell
def _():
    import marimo as mo
    from sortedcontainers import SortedDict, SortedList

    return SortedDict, SortedList, mo


@app.cell
def _(SortedList, mo):
    readings = SortedList([17, 3, 42, 8, 23])
    readings.add(11)
    _window = list(readings.irange(8, 23))
    mo.md(
        f"""
    ## SortedList

    `SortedList` keeps order on every mutation: `{list(readings)}`.

    - `readings.bisect_left(20)` → index `{readings.bisect_left(20)}`
    - `irange(8, 23)` iterates the closed range `{_window}` without scanning
    """
    )
    return


@app.cell
def _(SortedDict, mo):
    deadlines = SortedDict({"2026-09-01": "draft", "2026-06-15": "outline", "2026-12-01": "ship"})
    _next_up = deadlines.peekitem(0)
    mo.md(
        f"""
    ## SortedDict

    `SortedDict` iterates keys in order — `{list(deadlines)}` — so the nearest
    deadline is always `peekitem(0)` = `{_next_up}`. Range queries, order
    statistics, and nearest-neighbor lookups come free from the same index.
    """
    )
    return


if __name__ == "__main__":
    app.run()

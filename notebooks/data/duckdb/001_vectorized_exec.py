# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "duckdb",
# ]
# ///

"""duckdb — vectorized execution: relations, EXPLAIN, and the physical plan."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="duckdb: vectorized execution")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # duckdb: vectorized execution

    Seed notebook (taxonomy B2). The Python API angle — relations and
    `EXPLAIN` on the physical plan. (The `mo.sql()` cell angle lives in
    `notebooks/data/ibis/001_duckdb_sql.py`.)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/duckdb/duckdb>
    - Architecture corpus: the `duckdb` study (138 files) maps the vectorized
      engine (DataChunks, pipelines, the morsel-driven scheduler).
    - Taxonomy row: B2 in `notes/taxonomy.md`.
    """)
    return


@app.cell
def _():
    import duckdb
    import marimo as mo

    return duckdb, mo


@app.cell
def _(duckdb):
    con = duckdb.connect()
    totals = con.sql(
        """
        SELECT (range % 5) AS bucket,
               count(*)    AS n,
               sum(range)  AS total
        FROM range(1_000_000)
        GROUP BY bucket
        ORDER BY bucket
        """
    )
    return con, totals


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Vectorized aggregation
    """)
    return


@app.cell
def _(mo, totals):
    mo.ui.table(
        [dict(zip(totals.columns, row, strict=True)) for row in totals.fetchall()],
        label="1M rows aggregated into 5 buckets",
    )
    return


@app.cell
def _(con, mo):
    _plan = con.sql(
        "EXPLAIN SELECT (range % 5) AS bucket, sum(range) FROM range(1_000_000) GROUP BY bucket"
    ).fetchall()
    mo.md(
        f"""
    ## The physical plan

    `EXPLAIN` shows the physical operators that process data in vectors
    (DataChunks of ~2048 rows), not row-at-a-time:

    ```
    {_plan[0][1]}
    ```
    """
    )
    return


if __name__ == "__main__":
    app.run()

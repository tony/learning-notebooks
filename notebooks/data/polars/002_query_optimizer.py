# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "polars",
# ]
# ///

"""polars — the query optimizer: read .explain() and watch pushdown rewrite a plan."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="polars: the query optimizer")


with app.setup:
    import marimo as mo
    import polars as pl


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # polars: the query optimizer

    `polars/001` showed that `.lazy()` builds a plan instead of moving data.
    This notebook is about *what the optimizer does to that plan before it
    runs*. We build one query, print its plan **before** and **after**
    optimization, and watch two rewrites do the heavy lifting: **predicate
    pushdown** (filter at the scan) and **projection pushdown** (read only the
    columns you need). The same idea every analytical engine relies on — it is
    why lazy evaluation pays for itself.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/pola-rs/polars>
    - In the source: `crates/polars-plan/src/plans/optimizer/` (the passes:
      `predicate_pushdown/`, `projection_pushdown/`, `simplify_expr/`)
    - Architecture corpus: the `polars` study maps the 15-pass optimizer over
      the logical plan.
    - Concepts: lazy-evaluation, query-optimization, predicate-pushdown, projection-pushdown, columnar
    - See also: `notebooks/data/polars/001_lazy_frames.py` — the lazy API this
      builds on; `notebooks/data/duckdb/001_vectorized_exec.py` — EXPLAIN on a
      different engine; `notebooks/data/pyarrow/002_zero_copy_synergy.py` — the
      columnar buffers underneath
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## A small sales frame, built lazily

    Eight rows is enough — the plan, not the data size, is the lesson. `pl.LazyFrame`
    records the schema and the operations; nothing is computed yet.
    """)
    return


@app.cell
def _():
    sales = pl.LazyFrame(
        {
            "region": ["west", "east", "west", "east", "west", "east", "west", "east"],
            "product": ["a", "a", "b", "b", "a", "b", "a", "b"],
            "units": [10, 5, 7, 3, 2, 8, 6, 4],
            "unit_price": [9, 9, 4, 4, 9, 4, 9, 4],
        }
    )
    sales
    return (sales,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## One query, two plans

    We compute revenue, keep only the **west** region, and total revenue per
    product. `.explain(optimized=False)` is the plan as written, top-down;
    `.explain()` is what actually runs. Read both bottom-up (the scan is the
    leaf) and compare where the `FILTER` and the column list land.
    """)
    return


@app.cell
def _(sales):
    west_revenue = (
        sales.with_columns((pl.col("units") * pl.col("unit_price")).alias("revenue"))
        .filter(pl.col("region") == "west")
        .group_by("product")
        .agg(pl.col("revenue").sum())
        .sort("product")
    )
    return (west_revenue,)


@app.cell
def _(west_revenue):
    mo.md(
        f"""
    **Naive plan** — `.explain(optimized=False)` (the filter sits *above* the
    scan; every column is read):

    ```
    {west_revenue.explain(optimized=False)}
    ```

    **Optimized plan** — `.explain()` (the filter is now a `SELECTION` *inside*
    the scan, and `PROJECT` reads only the columns the query touches):

    ```
    {west_revenue.explain()}
    ```
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## What the passes did

    Two rewrites moved work toward the data:

    - **Predicate pushdown** — `region == "west"` became a `SELECTION` evaluated
      *as the frame is scanned*, so half the rows never enter the pipeline. On a
      Parquet/CSV scan this also skips row groups.
    - **Projection pushdown** — only `region`, `product`, `units`, `unit_price`
      are read; `revenue` is derived on the surviving rows. A wider table would
      drop every unused column at the source.

    Both are pure consequences of **lazy evaluation**: because polars sees the
    *whole* query before executing, it can rewrite it. An eager `DataFrame`
    runs each step as you type it and gets none of this.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## collect() runs the optimized plan
    """)
    return


@app.cell
def _(west_revenue):
    mo.ui.table(
        west_revenue.collect().to_dicts(),
        label="west-region revenue per product (the plan, executed)",
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## TODO(you)

    Add `.head(1)` to the end of the query and print `.explain()` again. Polars
    has a **slice pushdown** pass — does the limit reach the scan, and does the
    plan still compute the full `group_by` first? (It must: an aggregate can't be
    sliced early.) Predict before you print.
    """)
    return


@app.cell
def test_optimizer_pushes_down_without_changing_results():
    _sales = pl.LazyFrame(
        {
            "region": ["west", "east", "west", "east", "west", "east", "west", "east"],
            "product": ["a", "a", "b", "b", "a", "b", "a", "b"],
            "units": [10, 5, 7, 3, 2, 8, 6, 4],
            "unit_price": [9, 9, 4, 4, 9, 4, 9, 4],
        }
    )
    _q = (
        _sales.with_columns((pl.col("units") * pl.col("unit_price")).alias("revenue"))
        .filter(pl.col("region") == "west")
        .group_by("product")
        .agg(pl.col("revenue").sum())
        .sort("product")
    )
    # The optimizer rewrote the plan...
    assert _q.explain(optimized=False) != _q.explain()
    # ...but the answer is identical: west = {a: 90+18+54, b: 28}.
    _out = {row["product"]: row["revenue"] for row in _q.collect().to_dicts()}
    assert _out == {"a": 162, "b": 28}, _out
    return


if __name__ == "__main__":
    app.run()

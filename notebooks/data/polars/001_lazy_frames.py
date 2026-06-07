# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "polars",
# ]
# ///

"""polars — lazy frames: build a query plan, inspect it, then collect (B1, L2)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="polars: lazy frames")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # polars: lazy frames

    Seed notebook (taxonomy B1/B2). polars' lazy API builds a **logical plan**
    that the optimizer rewrites (predicate pushdown, projection pruning) before
    any data moves — `.explain()` shows the plan, `.collect()` executes it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/pola-rs/polars>
    - In the source: `crates/polars-plan/`
      (the logical plan this notebook prints)
    - Architecture corpus: the `polars` study maps the Rust query engine.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(pl):
    lazy_orders = (
        pl.LazyFrame(
            {
                "region": ["north", "south", "north", "east", "south", "north"],
                "units": [12, 7, 30, 5, 18, 9],
                "price": [2.5, 4.0, 1.25, 9.0, 3.5, 2.0],
            }
        )
        .with_columns(revenue=pl.col("units") * pl.col("price"))
        .filter(pl.col("units") > 6)
        .group_by("region")
        .agg(pl.col("revenue").sum().alias("total_revenue"))
        .sort("total_revenue", descending=True)
    )
    return (lazy_orders,)


@app.cell
def _(lazy_orders, mo):
    mo.md(
        f"""
    ## The plan, before any data moves

    Nothing has executed yet — `lazy_orders` is a plan. The optimizer's view:

    ```
    {lazy_orders.explain()}
    ```

    Note the `FILTER` sitting *below* the aggregation — pushed down toward the
    scan so fewer rows ever flow upward.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Collect: the optimized plan runs
    """)
    return


@app.cell
def _(lazy_orders):
    lazy_orders.collect()
    return


if __name__ == "__main__":
    app.run()

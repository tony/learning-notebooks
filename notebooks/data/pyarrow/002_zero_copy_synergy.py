# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "duckdb",
#     "marimo",
#     "pandas",
#     "polars",
#     "pyarrow",
# ]
# ///

"""pyarrow — zero-copy synergy: one Arrow table shared by polars, pandas, and duckdb."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="arrow: zero-copy synergy")


with app.setup:
    import duckdb
    import marimo as mo
    import pandas as pd
    import polars as pl
    import pyarrow as pa


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # One buffer, four engines (the synergy notebook)

    The reproducibility-and-synergy rung of the mastery ladder, made
    concrete: a single Arrow table is queried by **polars**, **pandas**, and
    **duckdb** in one sandbox — and the receipts (`pa.total_allocated_bytes`,
    buffer addresses) show the data was **never copied**. Interop through a
    shared memory format is what makes a multi-tool stack *one* system
    instead of an ETL chain.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/apache/arrow>
    - In the source: `cpp/src/arrow/array/` (the
      buffer layout every engine here agrees on)
    - Architecture corpus: the `arrow` study (120 files); `duckdb` and
      `polars` studies cover the consuming engines.
    - Concepts: zero-copy, columnar, vectorized-execution
    - See also: `notebooks/data/polars/001_lazy_frames.py` — the lazy engine
      that consumes these buffers
    """)
    return


@app.cell
def _():
    n_rows = 100_000
    readings = pa.table(
        {
            "sensor": pa.array(["alpha", "beta", "gamma", "delta"] * (n_rows // 4)),
            "units": pa.array(range(n_rows), type=pa.int64()),
            "price": pa.array([(i % 997) / 10 for i in range(n_rows)], type=pa.float64()),
        }
    )
    base_alloc = pa.total_allocated_bytes()
    price_addr = readings["price"].chunk(0).buffers()[1].address
    return base_alloc, price_addr, readings


@app.cell(hide_code=True)
def _():
    mo.mermaid(
        """
    graph LR
        BUF[("Arrow buffers<br/>(one allocation)")]
        BUF --> PL[polars DataFrame]
        BUF --> PD[pandas ArrowDtype]
        BUF --> DD[duckdb scan]
        BUF --> PA[pyarrow compute]
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The polars hop
    """)
    return


@app.cell
def _(base_alloc, price_addr, readings):
    pl_df = pl.from_arrow(readings)
    _delta = pa.total_allocated_bytes() - base_alloc
    _roundtrip_addr = pl_df.to_arrow()["price"].chunk(0).buffers()[1].address
    mo.vstack(
        [
            mo.md("**polars** wraps the buffers, computes vectorized, hands them back:"),
            mo.hstack(
                [
                    mo.stat(
                        value=f"{_delta:,} B",
                        label="new Arrow bytes after from_arrow",
                        bordered=True,
                    ),
                    mo.stat(
                        value="same" if _roundtrip_addr == price_addr else "different",
                        label="price buffer address after round-trip",
                        bordered=True,
                    ),
                    mo.stat(
                        value=f"{pl_df['price'].mean():.3f}",
                        label="pl mean(price)",
                        bordered=True,
                    ),
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (pl_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The pandas hop
    """)
    return


@app.cell
def _(base_alloc, readings):
    pd_arrow = readings.to_pandas(types_mapper=pd.ArrowDtype)
    _delta_arrow = pa.total_allocated_bytes() - base_alloc
    pd_numpy = readings.to_pandas()  # the copying path: numpy blocks + object strings
    mo.vstack(
        [
            mo.md(
                "**pandas** has both behaviors — `types_mapper=pd.ArrowDtype`"
                " keeps the Arrow buffers; the default materializes numpy"
                " blocks (strings become Python objects — the expensive part):"
            ),
            mo.hstack(
                [
                    mo.stat(
                        value=f"{_delta_arrow:,} B",
                        label="ArrowDtype path: new bytes",
                        bordered=True,
                    ),
                    mo.stat(
                        value=f"{int(pd_numpy.memory_usage(deep=True).sum()):,} B",
                        label="default path: numpy/object footprint",
                        caption="a full second copy",
                        bordered=True,
                    ),
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (pd_arrow,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The duckdb hop
    """)
    return


@app.cell
def _(readings):
    con = duckdb.connect()
    per_sensor = con.sql(
        """
        SELECT sensor, count(*) AS n, round(avg(price), 3) AS avg_price
        FROM readings
        GROUP BY sensor ORDER BY sensor
        """
    )
    mo.vstack(
        [
            mo.md(
                "**duckdb** never imports anything — its replacement scan reads"
                " the Arrow table variable in place, DataChunk by DataChunk:"
            ),
            mo.ui.table(
                [dict(zip(per_sensor.columns, row, strict=True)) for row in per_sensor.fetchall()]
            ),
        ],
        gap=0.5,
    )
    return (con,)


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "When copies DO happen": mo.md(
                """
    - pandas default `to_pandas()` — numpy consolidation; strings become
      Python objects (the footprint stat above is the bill)
    - any engine *mutating* shared buffers — Arrow arrays are immutable,
      so mutation forces copy-on-write somewhere
    - crossing type systems (Arrow dictionary → pandas categorical is
      cheap; → plain numpy strings is not)
    - and a subtle one this notebook's test pins down: polars hands back
      `large_string` (64-bit offsets, its native layout) where Arrow had
      `string` — the *numeric* buffers round-trip untouched, but string
      columns are re-framed. Zero-copy holds exactly where layouts agree.
    """
            ),
            "TODO(you): dictionary encoding": mo.md(
                """
    Re-build `sensor` as `pa.array([...]).dictionary_encode()` and re-run
    the hops. Which engines keep the dictionary intact (polars Categorical,
    duckdb ENUM-ish) and which expand it? Check the byte stats.
    """
            ),
        }
    )
    return


@app.cell
def test_one_system(con, pd_arrow, pl_df, price_addr, readings):
    # Numeric columns round-trip polars bit-identically — same buffers.
    _rt = pl_df.to_arrow()
    assert _rt["units"].equals(readings["units"])
    assert _rt["price"].chunk(0).buffers()[1].address == price_addr
    # Strings get re-framed to polars' native 64-bit-offset layout:
    assert pa.types.is_large_string(_rt.schema.field("sensor").type)
    # All four engines agree on the same aggregate over the same buffers.
    _pa_sum = float(pa.compute.sum(readings["price"]).as_py())
    _pl_sum = float(pl_df["price"].sum())
    _pd_sum = float(pd_arrow["price"].sum())
    _dd_sum = float(con.sql("SELECT sum(price) FROM readings").fetchone()[0])
    assert abs(_pa_sum - _pl_sum) < 1e-6
    assert abs(_pa_sum - _pd_sum) < 1e-6
    assert abs(_pa_sum - _dd_sum) < 1e-6
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - Storage formats: delta-rs puts these same buffers under ACID table semantics
    - Backlog (`notes/study_plan.md`): an end-to-end pipeline
      (pyarrow → duckdb → sklearn) with `mo.persistent_cache`
    """)
    return


if __name__ == "__main__":
    app.run()

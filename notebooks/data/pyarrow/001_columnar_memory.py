# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "pyarrow",
# ]
# ///

"""pyarrow — columnar memory: tables, chunks, and zero-copy slices."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="pyarrow: columnar memory")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # pyarrow: columnar memory

    Seed notebook (taxonomy B3/B4). Arrow is the interchange layer under
    pandas/polars/duckdb/spark — one columnar format, shared without copies.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/apache/arrow>
    - Architecture corpus: the `arrow` study (120 files) maps the columnar
      format, IPC, and compute kernels.
    - Taxonomy rows: B3/B4 in `notes/taxonomy.md`.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pyarrow as pa
    import pyarrow.compute as pc

    return mo, pa, pc


@app.cell
def _(mo, pa):
    readings = pa.table(
        {
            "sensor": ["a", "b", "a", "c", "b", "a"],
            "value": [1.5, 2.0, 0.75, 4.2, 3.3, 2.8],
        }
    )
    mo.md(
        f"""
    A `pa.Table` is a schema plus chunked columns — each column a sequence of
    immutable Arrow arrays:

    ```
    {readings.schema}
    ```

    `{readings.num_rows}` rows · `{readings.nbytes}` bytes ·
    column `value` has `{readings.column("value").num_chunks}` chunk(s).
    """
    )
    return (readings,)


@app.cell
def _(mo, pa, pc, readings):
    window = readings.slice(1, 3)
    summed = pc.sum(readings.column("value"))
    mo.md(
        f"""
    `slice(1, 3)` is **zero-copy** — it adjusts offsets into the same buffers
    (`{window.num_rows}` rows, still `{type(window).__name__}`), and compute
    kernels run vectorized over the buffers: `pc.sum(value)` =
    `{summed.as_py()}`.

    That buffer discipline is why pandas/polars/duckdb exchange Arrow data
    without serialization — `pa.total_allocated_bytes()` =
    `{pa.total_allocated_bytes()}` for everything above.
    """
    )
    return


if __name__ == "__main__":
    app.run()

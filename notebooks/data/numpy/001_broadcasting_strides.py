# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "numpy",
# ]
# ///

"""numpy — broadcasting & strides: how ndarray shapes combine and memory is viewed."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="numpy: broadcasting & strides")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # numpy: broadcasting & strides

    Seed notebook. Two ideas under every numpy expression:
    **broadcasting** (how shapes combine without copying) and **strides**
    (how one buffer is viewed many ways).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/numpy/numpy>
    - Architecture corpus: the `numpy` study (144 files) maps the C core.
    """)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    return mo, np


@app.cell
def _(mo, np):
    grid = np.arange(12).reshape(3, 4)
    col_offsets = np.array([[10], [20], [30]])
    shifted = grid + col_offsets
    mo.md(
        f"""
    ## Broadcasting

    Broadcasting aligns trailing dimensions: `{grid.shape} + {col_offsets.shape}`
    stretches the `(3, 1)` column across 4 columns **without materializing** the
    repeated data:

    ```
    {shifted!r}
    ```
    """
    )
    return (grid,)


@app.cell
def _(grid, mo, np):
    transposed = grid.T
    every_other_row = grid[::2]
    mo.md(
        f"""
    ## Strides and views

    Strides are the bytes to step per axis — views reinterpret, never copy:

    | array | shape | strides | owns memory? |
    |---|---|---|---|
    | `grid` | `{grid.shape}` | `{grid.strides}` | `{grid.base is None}` |
    | `grid.T` | `{transposed.shape}` | `{transposed.strides}` | `{transposed.base is None}` |
    | `grid[::2]` | `{every_other_row.shape}` | `{every_other_row.strides}` | `{every_other_row.base is None}` |

    Same buffer, three shapes — `np.shares_memory(grid, grid.T)` =
    `{np.shares_memory(grid, transposed)}`.
    """
    )
    return


if __name__ == "__main__":
    app.run()

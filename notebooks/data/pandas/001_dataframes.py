# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "pandas",
# ]
# ///

"""pandas — DataFrames: construction, dtypes, selection, and groupby."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="pandas: DataFrames")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # pandas: DataFrames

    First contact with the core data structure: how a DataFrame is built,
    what dtypes it infers, how selection works, and a first groupby.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/pandas-dev/pandas>
    - Start at `pandas/core/frame.py` (the `DataFrame` class).
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    return mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Construct a DataFrame
    """)
    return


@app.cell
def _(pd):
    penguins = pd.DataFrame(
        {
            "species": ["Adelie", "Adelie", "Gentoo", "Gentoo", "Chinstrap", "Chinstrap"],
            "island": ["Torgersen", "Biscoe", "Biscoe", "Biscoe", "Dream", "Dream"],
            "bill_length_mm": [39.1, 37.8, 46.1, 50.0, 46.5, 49.5],
            "body_mass_g": [3750, 3700, 4500, 5700, 3500, 3800],
        }
    )
    penguins
    return (penguins,)


@app.cell
def _(penguins):
    # Inferred dtypes: object for strings, float64/int64 for numerics.
    penguins.dtypes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Selection and groupby
    """)
    return


@app.cell
def _(penguins):
    # Label-based selection: .loc[rows, columns].
    penguins.loc[penguins["body_mass_g"] > 3700, ["species", "body_mass_g"]]
    return


@app.cell
def _(penguins):
    # Split-apply-combine: mean body mass per species.
    penguins.groupby("species")["body_mass_g"].mean()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The interactive table
    """)
    return


@app.cell
def _(mo, penguins):
    # marimo's interactive table: sort, filter, and column stats in the browser.
    mo.ui.table(penguins)
    return


if __name__ == "__main__":
    app.run()

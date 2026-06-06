# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""LIBRARY — TOPIC: one-line summary of what this notebook studies."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # LIBRARY: TOPIC

    What this notebook studies, and the questions it answers.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Source reading

    - Upstream: <https://github.com/ORG/REPO>
    - Local clone (sibling of this repo): `../REPO`
    """
    )
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    # Study code goes here. The last expression in a cell is its output.
    1 + 1
    return


if __name__ == "__main__":
    app.run()

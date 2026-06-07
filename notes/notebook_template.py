# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""LIBRARY — TOPIC: one-line summary of what this notebook studies."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="LIBRARY: TOPIC")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # LIBRARY: TOPIC

    What this notebook studies, and the questions it answers.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/ORG/REPO>
    - In the source: `path/within/the/repo/` (what this notebook studies)
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Study

    Rename this heading per teaching section — marimo's Outline panel
    navigates by markdown headings (keep them out of accordions/tabs).
    """)
    return


@app.cell
def _():
    # Study code goes here. The last expression in a cell is its output.
    #
    # Recipe — gate expensive work (CI-safe: the gated cell stays stopped headlessly):
    #   run = mo.ui.run_button(label="Train")        # cell A: the gate
    #   mo.stop(not run.value, mo.md("Click *Train*"))  # cell B: stops until clicked
    #   with mo.persistent_cache("train"):           # disk cache in gitignored __marimo__/
    #       model = expensive_training()
    # More recipes: notes/NOTEBOOK_TEMPLATE.md; exemplar: notebooks/toolchain/marimo/001_basics.py.
    1 + 1
    return


if __name__ == "__main__":
    app.run()

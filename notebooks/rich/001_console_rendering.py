# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "rich",
# ]
# ///

"""rich — console rendering: renderables, tables, and the console protocol."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # rich: console rendering

    rich renderables implement `__rich_console__` and (via `JupyterMixin`)
    `_repr_mimebundle_`, which marimo picks up — so a `Table` or `Panel` as a
    cell's last expression renders directly in the notebook.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Source reading

    - Upstream: <https://github.com/Textualize/rich>
    - Local clone (sibling of this repo): `../rich`
    - Start at `rich/console.py` (the render protocol) and `rich/jupyter.py`
      (`JupyterMixin`, which is what makes renderables notebook-aware).
    """
    )
    return


@app.cell
def _():
    import marimo as mo
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    return (Panel, Table, Text, mo)


@app.cell
def _(Table):
    table = Table(title="Render protocol members")
    table.add_column("Member", style="cyan")
    table.add_column("Role")
    table.add_row("__rich_console__", "yields renderable segments")
    table.add_row("__rich_measure__", "reports width requirements")
    table.add_row("_repr_mimebundle_", "notebook integration (JupyterMixin)")
    table
    return


@app.cell
def _(Panel, Text):
    Panel(Text("Styled text inside a panel", style="bold magenta"), title="rich.panel.Panel")
    return


if __name__ == "__main__":
    app.run()

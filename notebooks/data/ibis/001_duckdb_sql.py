# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ibis-framework[duckdb]",
#     "marimo[sql]",
# ]
# ///

"""ibis — DuckDB backend: expressions, lazy evaluation, and SQL interop."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="ibis: expressions on DuckDB")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # ibis: expressions on DuckDB

    ibis builds a typed expression tree that compiles to SQL. This notebook
    constructs expressions on the in-process DuckDB backend and compares them
    with the equivalent `mo.sql()` query.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/ibis-project/ibis>
    - Start at `ibis/expr/types/relations.py` (the `Table` expression class).
    """)
    return


@app.cell
def _():
    import ibis
    import marimo as mo

    ibis.options.interactive = True
    return ibis, mo


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Build an expression tree
    """)
    return


@app.cell
def _(ibis):
    penguins = ibis.memtable(
        {
            "species": ["Adelie", "Adelie", "Gentoo", "Gentoo", "Chinstrap", "Chinstrap"],
            "body_mass_g": [3750, 3700, 4500, 5700, 3500, 3800],
        }
    )
    penguins
    return (penguins,)


@app.cell
def _(penguins):
    # An expression, not a result: filtering + aggregation build an IR tree
    # that DuckDB executes only when the value is rendered.
    heavy = penguins.filter(penguins.body_mass_g > 3600)
    heavy.group_by("species").agg(avg_mass=heavy.body_mass_g.mean())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The compiled SQL
    """)
    return


@app.cell
def _(ibis, penguins):
    # Inspect the compiled SQL behind an expression.
    ibis.to_sql(penguins.group_by("species").agg(n=penguins.count()))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The same aggregation as a marimo SQL cell
    """)
    return


@app.cell
def _(mo, penguins_df):
    # The same aggregation as a marimo SQL cell (DuckDB over in-scope dataframes).
    mo.sql(
        """
        SELECT species, avg(body_mass_g) AS avg_mass
        FROM penguins_df
        GROUP BY species
        ORDER BY avg_mass DESC
        """
    )
    return


@app.cell
def _(penguins):
    # Materialize the ibis expression to pandas for the SQL cell above.
    penguins_df = penguins.to_pandas()
    return (penguins_df,)


if __name__ == "__main__":
    app.run()

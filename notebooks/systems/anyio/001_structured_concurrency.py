# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "anyio",
#     "marimo",
# ]
# ///

"""anyio — structured concurrency: task groups, timeouts, and cancellation scopes."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="anyio: structured concurrency")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # anyio: structured concurrency

    Seed notebook (taxonomy A3). anyio's core idea: concurrency has *scope* —
    tasks live inside a task group and **cannot outlive it**; cancellation is a
    scope you enter, not a flag you poll. marimo cells can be `async def`, so
    the demos below `await` natively.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/agronholm/anyio>
    - Deep dives live in `../learning-asyncio/notes/progression.md` (event loop
      fundamentals) and the `tokio`/`libuv` architecture studies (the same
      ideas in Rust/C).
    - Taxonomy row: A3 in `notes/taxonomy.md`.
    """)
    return


@app.cell
def _():
    import anyio
    import marimo as mo

    return anyio, mo


@app.cell
async def _(anyio, mo):
    _arrivals: list[str] = []

    async def _worker(name: str, delay: float) -> None:
        await anyio.sleep(delay)
        _arrivals.append(name)

    async with anyio.create_task_group() as _tg:
        _tg.start_soon(_worker, "tortoise", 0.10)
        _tg.start_soon(_worker, "hare", 0.02)
        _tg.start_soon(_worker, "snail", 0.15)

    mo.md(
        f"""
    A **task group** starts tasks concurrently and joins them all at the
    `async with` exit — completion order `{_arrivals}` differs from start
    order, but nothing escapes the block.
    """
    )
    return


@app.cell
async def _(anyio, mo):
    _progress: list[str] = []
    with anyio.move_on_after(0.05) as _scope:
        _progress.append("started slow work")
        await anyio.sleep(1.0)
        _progress.append("never reached")
    mo.md(
        f"""
    **Cancellation is a scope**: `move_on_after(0.05)` cancelled the
    1-second sleep — `cancelled_caught` = `{_scope.cancelled_caught}`,
    progress = `{_progress}`. No flags, no `Task.cancel()` bookkeeping;
    leaving the scope is the cancellation boundary.
    """
    )
    return


if __name__ == "__main__":
    app.run()

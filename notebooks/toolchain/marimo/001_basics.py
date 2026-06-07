# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""marimo — basics: a stdlib-only tour of marimo's bells and whistles."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="marimo basics")

with app.setup:
    # Setup cell: guaranteed to run before every other cell. Symbols defined
    # here are usable everywhere — including by top-level @app.function
    # definitions (see section 12) — without appearing in cell signatures.
    import asyncio
    import datetime as dt
    import time

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # marimo: basics

    A guided tour of marimo's feature surface using **only the Python standard
    library** (plus marimo itself). Each numbered section demonstrates one
    family of features:

    1. Reactivity & the dataflow graph
    2. UI widgets
    3. Composing widgets — `form`, `batch`, `array`, `dictionary`
    4. Layouts
    5. Markdown superpowers
    6. Control flow — gating expensive work
    7. Caching tiers
    8. State & output control
    9. Status elements
    10. Async & threads
    11. Modes & parameterization
    12. Reuse & testing
    13. CLI cheatsheet
    14. Further reading

    This file is also a teaching artifact about the *file format*: open it in a
    text editor to see the setup cell (`with app.setup:`), top-level functions
    (`@app.function`), named test cells, and `hide_code=True` prose cells.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/marimo-team/marimo>
    - In the source: `marimo/_tutorials/` (or `uvx marimo tutorial intro`)
    - Stdlib-only examples: `examples/misc/`
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 1. Reactivity & the dataflow graph

    marimo parses each cell **statically** and builds a DAG from the global
    names cells *define* and *reference*. Run a cell (or twiddle a widget) and
    every dependent cell re-runs automatically — page order is irrelevant.

    The next cell *reacts* to a variable defined **below** it.
    """)
    return


@app.cell(hide_code=True)
def _(changed):
    (
        mo.md(
            f"""
    **✨ Nice!** `changed` is now `{changed}` — this cell re-ran the instant
    you edited the cell below, because it *references* `changed`.
    """
        )
        if changed
        else mo.md(
            """
    **🌊 See it in action:** in the next cell, flip `changed` to `True` and
    run it. Watch *this* cell react.
    """
        )
    )
    return


@app.cell
def _():
    changed = False
    return (changed,)


@app.cell
def _(changed):
    mo.md(f"""
    Every cell knows its place in the graph: this one **references**
    `{mo.refs()}` and **defines** `{mo.defs()}` (via `mo.refs()` / `mo.defs()`).
    `changed` is `{changed}`.
    """)
    return


@app.cell
def _():
    _scratch = ["underscore", "variables"]
    mo.md(f"This cell's `_scratch`: `{_scratch}`")
    return


@app.cell
def _():
    _scratch = {"are": "cell-local"}
    mo.md(
        f"""
    Another cell's `_scratch`: `{_scratch}` — no collision! Globals must be
    **defined in exactly one cell**, but underscore-prefixed names are private
    to their cell.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Tip: execution order ≠ page order": (
                "marimo runs cells in dependency order, so you can put"
                " helper definitions at the bottom and headline results at"
                " the top. Section 6 below uses `fib` from section 12."
            ),
            "Tip: lazy runtime": (
                "In the notebook footer, switch *On Cell Change* from"
                " `autorun` to `lazy`: descendants are then only *marked*"
                " stale, which keeps expensive notebooks cheap to edit."
            ),
            "Tip: minimize mutations": (
                "marimo tracks *definitions*, not mutations. Mutate an object"
                " only in the cell that creates it — or derive a new variable"
                " (`df2 = df.assign(...)`) so the graph sees the change."
            ),
        }
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 2. UI widgets

    `mo.ui` ships ~30 widgets; everything below works with zero third-party
    dependencies. Interact with any of them and the gallery cell re-runs,
    showing the live `.value`.
    """)
    return


@app.cell
def _():
    slider = mo.ui.slider(0, 100, value=42, label="slider")
    range_slider = mo.ui.range_slider(0, 100, value=[20, 80], label="range_slider")
    number_input = mo.ui.number(0, 10, value=3, label="number")
    text_input = mo.ui.text(value="moss ball", label="text")
    text_area = mo.ui.text_area(value="multiple\nlines", label="text_area")
    code_editor = mo.ui.code_editor(value='print("hi")', language="python")
    checkbox = mo.ui.checkbox(value=True, label="checkbox")
    switch = mo.ui.switch(value=True, label="switch")
    radio = mo.ui.radio(["red", "green", "blue"], value="green", label="radio")
    dropdown = mo.ui.dropdown(["🍃", "🌊", "✨"], value="🍃", label="dropdown")
    multiselect = mo.ui.multiselect(
        ["pandas", "ibis", "rich", "marimo"], value=["marimo"], label="multiselect"
    )
    date_picker = mo.ui.date(value=dt.date(2026, 1, 1), label="date")
    click_counter = mo.ui.button(value=0, on_click=lambda count: count + 1, label="count my clicks")
    file_upload = mo.ui.file(label="file upload")
    return (
        checkbox,
        click_counter,
        code_editor,
        date_picker,
        dropdown,
        file_upload,
        multiselect,
        number_input,
        radio,
        range_slider,
        slider,
        switch,
        text_area,
        text_input,
    )


@app.cell
def _(
    checkbox,
    click_counter,
    code_editor,
    date_picker,
    dropdown,
    file_upload,
    multiselect,
    number_input,
    radio,
    range_slider,
    slider,
    switch,
    text_area,
    text_input,
):
    def _row(element):
        return mo.hstack(
            [element, mo.md(f"`{element.value!r}`")],
            justify="space-between",
            align="center",
            gap=2,
        )

    mo.ui.tabs(
        {
            "Numbers": mo.vstack([_row(slider), _row(range_slider), _row(number_input)]),
            "Text": mo.vstack([_row(text_input), _row(text_area), _row(code_editor)]),
            "Choices": mo.vstack([_row(radio), _row(dropdown), _row(multiselect)]),
            "Toggles": mo.vstack([_row(checkbox), _row(switch), _row(click_counter)]),
            "Date & files": mo.vstack([_row(date_picker), _row(file_upload)]),
        }
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Gotcha: a widget's value never updates in its own cell": (
                "Reading `slider.value` in the cell that *creates* the slider"
                " gives the initial value forever — re-running that cell would"
                " recreate the widget. Create widgets in one cell, read"
                " `.value` in another."
            )
        }
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 3. Composing widgets

    Chain `mo.md(...).batch(...)` to interpolate widgets into markdown, then
    `.form()` to gate everything behind a submit button. `mo.ui.array` and
    `mo.ui.dictionary` build *dynamic* collections of widgets.
    """)
    return


@app.cell
def _():
    study_form = (
        mo.md(
            """
    **Plan a study session**

    {topic}

    {minutes}

    {energy}
    """
        )
        .batch(
            topic=mo.ui.text(value="marimo", label="Topic"),
            minutes=mo.ui.slider(15, 120, step=15, value=45, label="Minutes"),
            energy=mo.ui.dropdown(["low", "medium", "high"], value="medium", label="Energy"),
        )
        .form(show_clear_button=True)
    )
    study_form
    return (study_form,)


@app.function
def render_study_plan(plan: dict) -> str:
    """Turn a submitted study form into a markdown study plan.

    TODO(you): shape the planning logic — e.g. split ``plan["minutes"]``
    into pomodoros sized by ``plan["energy"]``, schedule breaks, or veto
    marathon sessions. Return markdown.
    """
    return (
        f"Studying **{plan['topic']}** for **{plan['minutes']} min** at *{plan['energy']}* energy."
    )


@app.cell
def _(study_form):
    mo.stop(study_form.value is None, mo.md("⏳ *Submit the form above to generate a plan.*"))
    mo.md(render_study_plan(study_form.value))
    return


@app.cell
def _():
    reading_list = mo.ui.array(
        [mo.ui.text(value="reactivity"), mo.ui.text(value="caching")],
        label="reading list (add/remove rows)",
    )
    profile = mo.ui.dictionary(
        {
            "name": mo.ui.text(value="Ada"),
            "level": mo.ui.slider(1, 10, value=3),
        },
        label="profile",
    )
    mo.hstack([reading_list, profile], gap=2, justify="start")
    return profile, reading_list


@app.cell
def _(profile, reading_list):
    mo.md(f"""
    Live values — `reading_list.value`: `{reading_list.value}` ·
    `profile.value`: `{profile.value}`
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.callout(
        mo.md(
            "**Why not a plain `list`/`dict` of widgets?** marimo only syncs"
            " widgets bound to globals (or wrapped in `mo.ui.array` /"
            " `mo.ui.dictionary` / `.batch`). Widgets stuffed into ordinary"
            " containers render — but never update."
        ),
        kind="warn",
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 4. Layouts

    Stateless helpers arrange any objects — widgets, markdown, plain values.
    """)
    return


@app.cell
def _():
    _cards = [
        mo.callout(mo.md('`kind="neutral"`'), kind="neutral"),
        mo.callout(mo.md('`kind="info"`'), kind="info"),
        mo.callout(mo.md('`kind="success"`'), kind="success"),
        mo.callout(mo.md('`kind="warn"`'), kind="warn"),
        mo.callout(mo.md('`kind="danger"`'), kind="danger"),
    ]
    mo.vstack(
        [
            mo.md("`mo.callout` kinds, arranged with `mo.hstack(wrap=True)`:"),
            mo.hstack(_cards, gap=0.5, wrap=True, justify="start"),
        ]
    )
    return


@app.cell
def _():
    mo.hstack(
        [
            mo.stat(value="0.23.x", label="marimo", caption="pinned per-notebook", bordered=True),
            mo.stat(
                value=14,
                label="sections",
                caption="in this tour",
                direction="increase",
                bordered=True,
            ),
            mo.stat(value=0, label="third-party deps", caption="stdlib only", bordered=True),
        ],
        gap=1,
        widths="equal",
    )
    return


@app.cell
def _():
    mo.tree(
        {
            "layouts": ["hstack", "vstack", "accordion", "tabs", "carousel"],
            "alignment": ["center", "left", "right"],
            "app chrome": {"mention-only": ["sidebar", "nav_menu", "routes"]},
        },
        label="mo.tree renders nested data",
    )
    return


@app.cell
def _():
    mo.carousel(
        [
            mo.md("### Slide 1 — `mo.carousel` makes slideshows"),
            mo.callout("Slide 2 — any renderable works", kind="success"),
            mo.accordion(
                {
                    "Slide 3 — `mo.lazy` defers rendering": mo.lazy(
                        lambda: mo.md("💤 this markdown materialized only when revealed")
                    )
                }
            ),
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    App-chrome layouts not demoed here (they restructure the whole page):
    `mo.sidebar`, `mo.nav_menu`, `mo.routes` — see `docs/api/layouts/`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 5. Markdown superpowers

    `mo.md` is the workhorse: f-string interpolation of *any* object
    (including widgets), LaTeX, Mermaid diagrams, icons, and admonitions.
    """)
    return


@app.cell
def _(slider):
    mo.md(f"""
    f-strings make prose **dynamic**: the slider from section 2 currently
    reads **{slider.value}** — drag it and watch this sentence change.

    {"🍃" * (slider.value // 10 + 1)}
    """)
    return


@app.cell
def _():
    mo.md(r"""
    LaTeX renders out of the box:

    $$e^{i\pi} + 1 = 0 \qquad \varphi = \frac{1 + \sqrt{5}}{2}$$

    Inline too: reactivity is a topological sort over $G = (V, E)$.
    """)
    return


@app.cell
def _():
    mo.mermaid(
        """
    graph LR
        W[define widgets] --> G[render gallery]
        C["changed = False"] --> P[reactive prose]
        F["@app.function fib"] --> B[run_button gate]
        F --> T[test cell]
    """
    )
    return


@app.cell
def _():
    mo.md(f"""
    Iconify icons ({mo.icon("lucide:leaf")} {mo.icon("lucide:rocket", color="orange")}
    {mo.icon("lucide:flask-conical", color="teal")}) via `mo.icon("lucide:leaf")`.

    /// admonition | Admonitions, too.
    Write `/// admonition | Title` blocks inside `mo.md` for callout-style prose.
    ///
    """)
    return


@app.cell
def _():
    _payload = {"library": "marimo", "stdlib_only": True, "widgets": ["slider", "form"]}
    mo.vstack(
        [
            mo.md("Renderers for raw objects:"),
            mo.json(_payload),
            mo.plain_text(f"mo.plain_text: {_payload!r}"),
            mo.Html("<b>mo.Html</b> renders raw HTML; <code>mo.as_html(obj)</code> converts."),
            mo.inspect(dt.date(2026, 1, 1)),
        ],
        gap=0.5,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 6. Control flow — gating expensive work

    The canonical recipe: `mo.ui.run_button()` + `mo.stop()`. The gated cell
    halts until the button is clicked — in headless script runs it simply
    stays gated, which is what keeps this notebook CI-safe.
    """)
    return


@app.cell
def _():
    expensive_button = mo.ui.run_button(label="Compute fib(200) (pretend it's expensive)")
    expensive_button
    return (expensive_button,)


@app.cell
def _(expensive_button):
    mo.stop(
        not expensive_button.value,
        mo.md("👆 *This cell is gated: click the button above to run it.*"),
    )
    mo.md(f"`fib(200)` = `{fib(200)}` — note: `fib` is defined in **section 12**, below.")
    return


@app.cell
def _():
    ticker = mo.ui.refresh(options=["1s", "5s", "30s"])
    mo.hstack(
        [mo.md("`mo.ui.refresh` re-runs dependents on a timer (opt-in):"), ticker],
        justify="start",
        gap=1,
    )
    return (ticker,)


@app.cell
def _(ticker):
    ticker
    mo.md(f"Last refreshed at **{dt.datetime.now():%H:%M:%S}**.")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 7. Caching tiers

    Three levels: `@mo.cache` (unbounded, in-memory), `@mo.lru_cache(maxsize=…)`
    (bounded), and `mo.persistent_cache` (on disk in `__marimo__/cache/`,
    survives kernel restarts — ideal for model downloads and long training).
    """)
    return


@app.function
@mo.cache
def slow_square(n: int) -> int:
    time.sleep(0.05)
    return n * n


@app.cell
def _():
    _t0 = time.perf_counter()
    slow_square(12)
    _cold_ms = (time.perf_counter() - _t0) * 1000
    _t0 = time.perf_counter()
    slow_square(12)
    _warm_ms = (time.perf_counter() - _t0) * 1000
    mo.md(
        f"""
    `@mo.cache` memoization: cold call **{_cold_ms:.1f} ms** → cached call
    **{_warm_ms:.3f} ms**.
    """
    )
    return


@app.cell
def _():
    with mo.persistent_cache("leibniz_pi"):
        pi_approx = 4 * sum((-1) ** _k / (2 * _k + 1) for _k in range(200_000))
    mo.md(
        f"""
    `mo.persistent_cache("leibniz_pi")` cached `pi_approx = {pi_approx:.6f}`
    to disk — re-running the notebook (even after a restart) loads it instead
    of recomputing. The cache lives in `__marimo__/`, which this repo
    gitignores.
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 8. State & output control

    `mo.state` gives you a `(getter, setter)` pair: calling the setter re-runs
    every *other* cell that references the getter. It's the escape hatch for
    cycles (e.g. tally counters, undo stacks) — **prefer plain reactivity**
    for everything else.
    """)
    return


@app.cell
def _():
    get_tally, set_tally = mo.state(0)
    return get_tally, set_tally


@app.cell
def _(get_tally, set_tally):
    tally_button = mo.ui.button(
        label="increment the tally",
        on_click=lambda _: set_tally(get_tally() + 1),
    )
    tally_button
    return


@app.cell
def _(get_tally):
    mo.md(f"""
    Current tally: **{get_tally()}**
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.callout(
        mo.md(
            "**Best practice:** don't reach for `mo.state` or `on_change`"
            " handlers when referencing a widget's `.value` in another cell"
            " already does the job — 99% of notebooks never need state."
        ),
        kind="info",
    )
    return


@app.cell
def _():
    mo.output.append(mo.md("`mo.output.append` builds a cell's output **incrementally**…"))
    mo.output.append(
        mo.callout("…appending mid-execution. `mo.output.replace` swaps it.", kind="info")
    )
    return


@app.cell
def _():
    with mo.capture_stdout() as _buffer:
        print("this print never reaches the console panel")
    mo.md(
        f"""
    `mo.capture_stdout` captured: `{_buffer.getvalue().strip()}` — handy for
    studying libraries that print. (Uncaptured `print` output lands in the
    cell's *console* area, below the output.)
    """
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 9. Status elements

    `mo.status.progress_bar` wraps any iterable (like `tqdm`);
    `mo.status.spinner` is the indeterminate context-manager cousin.
    """)
    return


@app.cell
def _():
    for _ in mo.status.progress_bar(
        range(10), title="Crunching", subtitle="stdlib-only work", show_eta=True, show_rate=True
    ):
        time.sleep(0.02)
    mo.md("Done — watch the bar fill when this cell re-runs.")
    return


@app.cell
def _():
    with mo.status.spinner(title="Pretending to work…", subtitle="0.1 s of sleep"):
        time.sleep(0.1)
    mo.md("The spinner showed while the `with` block ran.")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 10. Async & threads

    Cells can be `async def` — the kernel awaits them natively. For
    background work, `mo.Thread` is a drop-in `threading.Thread` whose
    output streams are forwarded to the spawning cell (a plain
    `threading.Thread`'s output is lost).
    """)
    return


@app.cell
async def _():
    _t0 = time.perf_counter()
    await asyncio.sleep(0.05)
    mo.md(
        f"""
    This `async` cell awaited `asyncio.sleep` for
    **{(time.perf_counter() - _t0) * 1000:.0f} ms** without blocking the kernel.
    """
    )
    return


@app.cell
def _():
    _log: list[str] = []
    _worker = mo.Thread(target=lambda: _log.append("computed off the main thread"))
    _worker.start()
    _worker.join()
    mo.md(f"`mo.Thread` reported: *{_log[0]}*")
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 11. Modes & parameterization

    One file, four runtimes: the editor (`marimo edit`), an app
    (`marimo run`), a script (`python` / `uv run`), and a test suite
    (`pytest`). Cells can introspect and branch on the mode.
    """)
    return


@app.cell
def _():
    mo.vstack(
        [
            mo.md(
                f"**mode** = `{mo.app_meta().mode}` · **theme** = `{mo.app_meta().theme}` ·"
                f" **in notebook?** `{mo.running_in_notebook()}`"
            ),
            mo.md(
                f"**cli args** = `{mo.cli_args()}` — pass extras after `--`,"
                " e.g. `uv run 001_basics.py -- --limit 5`, read with"
                " `mo.cli_args().get('limit')`"
            ),
            mo.md(f"**query params** = `{mo.query_params()}` — read/write the app URL"),
            mo.md(
                f"**notebook dir** = `…/{mo.notebook_dir().name if mo.notebook_dir() else '?'}`"
                " via `mo.notebook_dir()`"
            ),
        ],
        gap=0.5,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 12. Reuse & testing

    A cell containing a single function that only references setup-cell
    symbols is serialized **top-level** with `@app.function` — importable
    from other modules and visible to plain `pytest`. Cells named `test_*`
    become pytest tests:

    ```bash
    uv run --with pytest pytest notebooks/toolchain/marimo/001_basics.py
    ```

    (One wrinkle: `001_basics` isn't a valid identifier, so regular
    `import` needs `importlib`; pytest handles it fine.)
    """)
    return


@app.function
def fib(n: int) -> int:
    """Return the n-th Fibonacci number; fib(0) == 0, fib(1) == 1."""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.cell
def test_fibonacci_basics():
    # TODO(you): which properties of fib deserve a test? Extend these.
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(10) == 55
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 13. CLI cheatsheet
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Editing & running": mo.md(
                """
    ```bash
    uvx marimo edit --sandbox nb.py   # edit in an isolated uv env (PEP 723)
    uvx marimo run nb.py              # serve as a read-only web app
    uv run nb.py                      # run headlessly as a script
    uvx marimo new                    # blank notebook (or: marimo new "prompt")
    ```
    """
            ),
            "Quality & conversion": mo.md(
                """
    ```bash
    uvx marimo check nb.py            # marimo's notebook-aware linter
    uvx marimo export html nb.py      # also: ipynb, script, md, html-wasm
    uvx marimo convert nb.ipynb       # Jupyter → marimo
    ```
    """
            ),
            "Learning": mo.md(
                """
    ```bash
    uvx marimo tutorial intro         # also: dataflow, ui, markdown, layout,
                                      # plots, sql, fileformat, for-jupyter-users
    ```
    """
            ),
            "Power features (pointers)": mo.md(
                """
    - **App composition**: `app.embed()` nests one notebook in another,
      with parameter substitution (marimo ≥ 0.19).
    - **WASM sharing**: `marimo export html-wasm`, or paste into
      <https://marimo.app> — runs entirely in the browser.
    - **Agent pairing**: `marimo pair` drops a coding agent into a live
      kernel session (marimo ≥ 0.23).
    """
            ),
        }
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## 14. Further reading

    - Best practices: `docs/guides/best_practices.md`
    - Reactivity model: `docs/guides/reactivity.md`
    - Expensive notebooks: `docs/guides/expensive_notebooks.md`
    - Reusing functions: `docs/guides/reusing_functions.md`
    - Testing: `docs/guides/testing/`
    - Online docs: <https://docs.marimo.io>
    """)
    return


if __name__ == "__main__":
    app.run()

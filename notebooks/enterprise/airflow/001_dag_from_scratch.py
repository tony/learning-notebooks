# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""airflow — a DAG scheduler from scratch: graphlib, retries, idempotent re-runs."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="enterprise: DAG scheduler from scratch")


with app.setup:
    from graphlib import TopologicalSorter

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # An orchestrator in ~40 lines

    Airflow's core is three ideas: a **dependency DAG** (stdlib `graphlib`
    sorts it), **retries with backoff** (failures are scheduled work, not
    exceptions), and an **idempotent run ledger** (re-running a finished
    pipeline does nothing). Build them small, and the production system
    becomes legible.

    Meta-note: you are *inside* one — marimo schedules this notebook's cells
    with exactly these invariants.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/apache/airflow>
    - In the source: the scheduler loop in
      `airflow-core/src/airflow/jobs/scheduler_job_runner.py` (or
      `airflow/jobs/` in older layouts) is this notebook at production scale
    - Architecture corpus: the `airflow` study (77 files); `dask`/`ray`
      studies cover task graphs for *compute* rather than *workflows*.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.mermaid(
        """
    graph LR
        extract --> validate
        extract --> transform
        validate --> load
        transform --> load
        load --> report
    """
    )
    return


@app.class_definition
class MiniScheduler:
    """A workflow scheduler: topological order + retries + a run ledger."""

    def __init__(self, max_retries: int = 2, backoff_base: int = 10) -> None:
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.ledger: list[dict] = []  # (task, attempt, status, sim_time)
        self.done: set[str] = set()
        self.clock = 0  # simulated seconds

    def run(self, dag: dict[str, set[str]], tasks: dict) -> None:
        """Execute `dag` (task -> deps) calling tasks[name](); retry failures."""
        sorter = TopologicalSorter(dag)
        for name in sorter.static_order():
            if name in self.done:  # idempotent re-run: ledger says skip
                self.ledger.append(
                    {"task": name, "attempt": 0, "status": "skipped", "t": self.clock}
                )
                continue
            for attempt in range(1, self.max_retries + 2):
                self.clock += 1  # the task takes a second
                try:
                    tasks[name]()
                except RuntimeError:
                    status = "retry" if attempt <= self.max_retries else "failed"
                    self.ledger.append(
                        {"task": name, "attempt": attempt, "status": status, "t": self.clock}
                    )
                    if status == "failed":
                        msg = f"{name} exhausted retries"
                        raise RuntimeError(msg) from None
                    self.clock += self.backoff_base * 2 ** (attempt - 1)  # backoff
                else:
                    self.done.add(name)
                    self.ledger.append(
                        {"task": name, "attempt": attempt, "status": "ok", "t": self.clock}
                    )
                    break


@app.function
def build_demo() -> tuple[dict[str, set[str]], dict, list[str]]:
    """The pipeline above; `transform` fails on its first attempt (flaky by design)."""
    effects: list[str] = []
    flaky_state = {"failures_left": 1}

    def task(name: str):
        def _run() -> None:
            if name == "transform" and flaky_state["failures_left"] > 0:
                flaky_state["failures_left"] -= 1
                msg = "transient transform error"
                raise RuntimeError(msg)
            effects.append(name)

        return _run

    dag: dict[str, set[str]] = {
        "extract": set(),
        "validate": {"extract"},
        "transform": {"extract"},
        "load": {"validate", "transform"},
        "report": {"load"},
    }
    return dag, {name: task(name) for name in dag}, effects


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Run it twice
    """)
    return


@app.cell
def _():
    sched = MiniScheduler()
    dag, tasks, effects = build_demo()
    sched.run(dag, tasks)
    sched.run(dag, tasks)  # second run: the ledger makes it a no-op
    return effects, sched


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The run ledger
    """)
    return


@app.cell
def _(sched):
    mo.vstack(
        [
            mo.md(
                "**The run ledger** — `transform` fails once, backs off 10"
                " simulated seconds, succeeds on attempt 2; the second pipeline"
                " run is all `skipped`:"
            ),
            mo.ui.table(sched.ledger),
        ],
        gap=0.5,
    )
    return


@app.cell
def _(effects, sched):
    mo.hstack(
        [
            mo.stat(
                value=len(effects), label="effects executed", caption="once each", bordered=True
            ),
            mo.stat(
                value=sum(1 for e in sched.ledger if e["status"] == "skipped"),
                label="skips on re-run",
                bordered=True,
            ),
            mo.stat(value=f"{sched.clock}s", label="simulated wall clock", bordered=True),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "What Airflow adds to these 40 lines": mo.md(
                """
    Persistence (the ledger becomes a database), distribution (executors
    fan tasks to workers), time (schedules + data intervals + backfills),
    and a UI. The *invariants* — topological order, retry budgets,
    idempotent task instances — are the ones you just read.
    """
            ),
            "Same DAG, three systems": mo.md(
                """
    - **marimo**: cells, sorted by variable dependencies — reactive re-run
    - **dask/ray**: compute tasks, sorted for parallel throughput
    - **airflow**: workflow tasks, sorted for orchestration with time

    One data structure, three execution policies.
    """
            ),
            "TODO(you): parallel waves": mo.md(
                """
    `static_order()` serializes everything. Switch to the incremental API
    (`prepare()` / `get_ready()` / `done()`) and group tasks into waves
    that *could* run concurrently — `validate` and `transform` should
    share a wave. How does the simulated clock change?
    """
            ),
        }
    )
    return


@app.cell
def test_scheduler(effects, sched):
    # Each effect ran exactly once despite the flaky failure + full re-run.
    assert sorted(effects) == ["extract", "load", "report", "transform", "validate"]
    # Dependencies were honored.
    assert effects.index("extract") < effects.index("transform") < effects.index("load")
    assert effects.index("load") < effects.index("report")
    # The flake retried with backoff and then succeeded.
    _transform = [e for e in sched.ledger if e["task"] == "transform"]
    assert [e["status"] for e in _transform] == ["retry", "ok", "skipped"]
    # Backoff actually advanced the simulated clock by 10s between attempts.
    assert _transform[1]["t"] - _transform[0]["t"] == 11
    # Second run touched nothing.
    assert sum(1 for e in sched.ledger if e["status"] == "skipped") == 5
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - The messaging relay (`enterprise/kafka/001_event_patterns.py`) is exactly the
      kind of task this scheduler should own
    - Backlog: real Airflow against these semantics; dask for the
      compute-DAG sibling
    """)
    return


if __name__ == "__main__":
    app.run()

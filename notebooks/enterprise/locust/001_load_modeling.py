# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""locust — load modeling from first principles: percentiles, Little's law, saturation (F3, L4)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="enterprise: load modeling")


with app.setup:
    import heapq
    import math
    import random
    import statistics

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # What a load test measures, before you run one

    Load tools (locust, jmeter, vegeta) sample two distributions — arrivals
    and service times — and report percentiles. This notebook builds the
    queueing model itself: a discrete-event simulation of `c` servers,
    **Little's law** (`L = λW`) verified numerically, and the saturation
    curve that explains why p95 explodes long before CPUs hit 100%.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/locustio/locust>
    - Local clone (relative): `../locust` — `locust/stats.py` (these same
      percentiles, harvested from real requests), `locust/runners.py`
    - Architecture corpus: `locust` (181 files), `jmeter`, `vegeta`,
      `hyperfine` — four harnesses, one queueing theory.
    - Taxonomy row: F3 · mastery L4 in `notes/taxonomy.md`.
    """)
    return


@app.function
def simulate_queue(
    arrival_rate: float, servers: int, n_requests: int = 4000, seed: int = 3
) -> dict:
    """Discrete-event M/G/c queue: Poisson arrivals, lognormal service times.

    Returns measured latencies, time-averaged concurrency L (by event
    integration), arrival rate, and mean latency W — the Little's law
    ingredients, all measured independently.
    """
    rng = random.Random(seed)
    mu, sigma = math.log(0.05), 0.5  # E[S] = exp(mu + sigma^2/2) ~ 56.7 ms
    free_at = [0.0] * servers
    heapq.heapify(free_at)
    clock = 0.0
    latencies: list[float] = []
    events: list[tuple[float, int]] = []
    for _ in range(n_requests):
        clock += rng.expovariate(arrival_rate)
        service = rng.lognormvariate(mu, sigma)
        start = max(clock, heapq.heappop(free_at))
        finish = start + service
        heapq.heappush(free_at, finish)
        latencies.append(finish - clock)
        events.append((clock, +1))
        events.append((finish, -1))
    events.sort()
    area = in_system = 0.0
    prev = events[0][0]
    for t, delta in events:
        area += in_system * (t - prev)
        in_system += delta
        prev = t
    duration = events[-1][0] - events[0][0]
    return {
        "latencies": latencies,
        "L": area / duration,
        "lam": n_requests / duration,
        "W": statistics.fmean(latencies),
        "expected_service": math.exp(mu + sigma**2 / 2),
    }


@app.cell
def _():
    arrival = mo.ui.slider(20, 139, step=1, value=60, label="arrival rate λ (req/s)")
    servers = mo.ui.slider(1, 16, value=8, label="servers c")
    mo.hstack([arrival, servers], gap=2, justify="start")
    return arrival, servers


@app.cell
def _(arrival, servers):
    sim = simulate_queue(arrival.value, servers.value)
    rho = arrival.value * sim["expected_service"] / servers.value
    _q = statistics.quantiles(sim["latencies"], n=100)
    mo.hstack(
        [
            mo.stat(value=f"{rho:.0%}", label="utilization rho = λE[S]/c", bordered=True),
            mo.stat(value=f"{_q[49] * 1000:.0f} ms", label="p50 latency", bordered=True),
            mo.stat(value=f"{_q[94] * 1000:.0f} ms", label="p95", bordered=True),
            mo.stat(value=f"{_q[98] * 1000:.0f} ms", label="p99", bordered=True),
        ],
        gap=1,
    )
    return (sim,)


@app.cell
def _(sim):
    _lw = sim["lam"] * sim["W"]
    mo.callout(
        mo.md(
            f"**Little's law, measured three ways**: time-averaged concurrency"
            f" `L = {sim['L']:.2f}` vs `λ·W = {sim['lam']:.1f} x {sim['W'] * 1000:.1f} ms"
            f" = {_lw:.2f}` — independent measurements, same number. It holds"
            " for ANY arrival/service distribution, which is why capacity math"
            " survives messy reality."
        ),
        kind="success",
    )
    return


@app.cell
def _(servers):
    _rows = []
    for _lam in (40, 70, 100, 125, 132, 137):
        _s = simulate_queue(_lam, servers.value)
        _rho = _lam * _s["expected_service"] / servers.value
        _qq = statistics.quantiles(_s["latencies"], n=100)
        _rows.append(
            {
                "λ (req/s)": _lam,
                "rho": f"{_rho:.0%}",
                "p50 (ms)": round(_qq[49] * 1000),
                "p95 (ms)": round(_qq[94] * 1000),
                "p99 (ms)": round(_qq[98] * 1000),
            }
        )
    mo.vstack(
        [
            mo.md(
                "**The saturation curve** — service time never changed; only"
                " *queueing* did. Past ~85% utilization the tail goes"
                " nonlinear, which is why SLOs are written against p95/p99:"
            ),
            mo.ui.table(_rows),
        ],
        gap=0.5,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "From model to measurement": mo.md(
                """
    locust replaces `rng.lognormvariate` with your actual service and
    `expovariate` with simulated users:
    `locust -f loadtest.py --host ...` against the fastapi endpoint from
    `ai_serving/fastapi/001_model_endpoint.py` served by uvicorn. The
    percentile table it prints is this notebook's table with reality as
    the random source.
    """
            ),
            "TODO(you): capacity planning": mo.md(
                """
    Your SLO is p95 < 150 ms at λ = 110 req/s. Using the sliders (or a
    sweep over `servers`), find the minimum `c` that meets it — then
    explain why the answer is not simply `λ·E[S]` rounded up.
    """
            ),
        }
    )
    return


@app.cell
def test_queueing(sim):
    # Little's law holds within sampling tolerance.
    assert abs(sim["L"] - sim["lam"] * sim["W"]) / sim["L"] < 0.05
    # Percentiles are ordered.
    _q = statistics.quantiles(sim["latencies"], n=100)
    assert _q[49] <= _q[94] <= _q[98]
    # Saturation: same servers, same service times, near-capacity load —
    # only queueing changes, and it more than doubles the tail.
    _lo = simulate_queue(40, 8)
    _hi = simulate_queue(137, 8)
    _p95_lo = statistics.quantiles(_lo["latencies"], n=100)[94]
    _p95_hi = statistics.quantiles(_hi["latencies"], n=100)[94]
    assert _p95_hi > 2 * _p95_lo, (_p95_lo, _p95_hi)
    assert _hi["W"] > 1.5 * _lo["W"]
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - Point a real harness at `ai_serving/fastapi/001_model_endpoint.py`
      (served, not TestClient) and compare its percentile table to the model
    - `hyperfine` (corpus ✦) is the single-command cousin for CLI latency
    """)
    return


if __name__ == "__main__":
    app.run()

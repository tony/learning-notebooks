# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "fastapi",
#     "httpx",
#     "marimo",
# ]
# ///

"""fastapi — a model endpoint, exercised in-process: schemas, validation, latency."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="serving: fastapi model endpoint")


with app.setup:
    import statistics
    import time

    import marimo as mo
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field


@app.class_definition
class ScoreRequest(BaseModel):
    """The endpoint's input contract — pydantic validates it before our code runs."""

    text: str = Field(min_length=1, max_length=2_000)
    threshold: float = Field(default=0.5, ge=0.0, le=1.0)


@app.class_definition
class ScoreResponse(BaseModel):
    """The output contract — serialization is part of the API, not an afterthought."""

    label: str
    score: float


@app.function
def stub_score(text: str) -> float:
    """Stand-in for a real model: keyword evidence squashed into [0, 1]."""
    positives = ("love", "great", "excellent", "happy", "wonderful")
    hits = sum(word in text.lower() for word in positives)
    return min(0.5 + 0.2 * hits, 1.0) if hits else 0.25


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # The API layer: a model endpoint without a server process

    E3's job is the boundary: typed request in, typed response out,
    validation errors for free. FastAPI's `TestClient` drives the ASGI app
    **in-process** — real routing, real pydantic validation, real status
    codes, no port, no subprocess — which is also exactly how you unit-test
    a service. CI-safe by construction.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/fastapi/fastapi>
    - In the source: `fastapi/routing.py` (how a
      function becomes an endpoint), `fastapi/dependencies/` (the DI graph)
    - Sibling curriculum: `../learning-fastapi/` (repo exists; notes pending)
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The endpoint
    """)
    return


@app.cell
def _():
    api = FastAPI(title="stub-scorer")

    @api.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @api.post("/score")
    def score(req: ScoreRequest) -> ScoreResponse:
        value = stub_score(req.text)
        return ScoreResponse(label="pos" if value >= req.threshold else "neg", score=value)

    client = TestClient(api)
    return (client,)


@app.cell
def _(client):
    _health = client.get("/health")
    _good = client.post("/score", json={"text": "I love this excellent library"})
    _invalid = client.post("/score", json={"threshold": 0.4})  # missing required text
    mo.ui.table(
        [
            {"call": "GET /health", "status": _health.status_code, "body": str(_health.json())},
            {"call": "POST /score (valid)", "status": _good.status_code, "body": str(_good.json())},
            {
                "call": "POST /score (missing text)",
                "status": _invalid.status_code,
                "body": str(_invalid.json()["detail"][0]["msg"]),
            },
        ]
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Validation for free

    The 422 above cost zero lines of our code — the request model *is* the
    validation. That contract-first habit is most of what separates a
    service from a script with a port.
    """)
    return


@app.cell
def _():
    live_text = mo.ui.text(value="what a wonderful day", label="score some text", full_width=True)
    live_text
    return (live_text,)


@app.cell
def _(client, live_text):
    _resp = client.post("/score", json={"text": live_text.value or "…"}).json()
    mo.callout(
        mo.md(
            f"**{_resp['label']}** · score `{_resp['score']:.2f}` — straight through the endpoint"
        ),
        kind="success" if _resp["label"] == "pos" else "neutral",
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Latency, in-process
    """)
    return


@app.cell
def _(client):
    _times: list[float] = []
    for _ in range(200):
        _t0 = time.perf_counter()
        client.post("/score", json={"text": "benchmark request"})
        _times.append((time.perf_counter() - _t0) * 1000)
    _q = statistics.quantiles(_times, n=100)
    mo.hstack(
        [
            mo.stat(value=f"{_q[49]:.2f} ms", label="p50 (in-process)", bordered=True),
            mo.stat(value=f"{_q[94]:.2f} ms", label="p95", bordered=True),
            mo.stat(
                value="200",
                label="requests",
                caption="routing + validation + serialization",
                bordered=True,
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "From TestClient to production": mo.md(
                """
    The same `api` object serves for real with
    `uvicorn module:api --workers 4`. What changes is everything *around*
    it: a process manager, `enterprise/locust/001_load_modeling.py`'s
    percentiles measured over a network, tracing (opentelemetry — the E3
    backlog), and the gateway patterns in domain F.
    """
            ),
            "TODO(you): cost accounting": mo.md(
                """
    Add a `tokens_estimated` field to `ScoreResponse` (len(text)//4 is the
    classic rough cut) and a middleware that accumulates a running
    cost-per-request counter. Where should that state live so workers
    don't disagree?
    """
            ),
        }
    )
    return


@app.cell
def test_endpoint_contract(client):
    _ok = client.post("/score", json={"text": "I love this", "threshold": 0.5})
    assert _ok.status_code == 200
    _body = _ok.json()
    assert _body["label"] == "pos" and 0.0 <= _body["score"] <= 1.0
    # Validation is part of the contract: missing text -> 422, not a crash.
    assert client.post("/score", json={"threshold": 0.9}).status_code == 422
    # Bounds enforced by the schema, not by our function.
    assert client.post("/score", json={"text": "x", "threshold": 2.0}).status_code == 422
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - F3 measures this endpoint under load: `enterprise/locust/001_load_modeling.py`
    - Swap `stub_score` for a real model behind `@mo.persistent_cache` and the
      contract doesn't change — that's the point
    """)
    return


if __name__ == "__main__":
    app.run()

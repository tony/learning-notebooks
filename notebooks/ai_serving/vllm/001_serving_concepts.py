# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""vllm — serving concepts, simulated: KV-cache memory and continuous batching (E1, L1)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="serving: KV-cache & batching")


with app.setup:
    import random

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Why LLM serving is a memory problem (simulated, stdlib-only)

    Two ideas explain most of vLLM: the **KV cache** (every generated token
    must re-read the keys/values of every previous token, so they're cached —
    and the cache, not the weights, is what fills the GPU) and **continuous
    batching** (refill finished slots every step instead of waiting for the
    batch's longest sequence). Both are arithmetic; this notebook computes
    them live. The real engine is the source reading.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/vllm-project/vllm>
    - Local clone (relative): `../vllm` — `vllm/core/` (the scheduler and
      block manager that make paged attention real), `vllm/attention/`
    - Architecture corpus: the `vllm` study (64 files); `ollama` (70) is the
      local-first counterpart.
    - Taxonomy row: E1 · mastery L1 in `notes/taxonomy.md`.
    """)
    return


@app.function
def kv_cache_bytes(
    seq_len: int, batch: int, layers: int = 32, kv_heads: int = 8, head_dim: int = 128
) -> int:
    """KV-cache size: 2 (K and V) x layers x kv_heads x head_dim x 2 bytes (fp16)."""
    return 2 * layers * kv_heads * head_dim * 2 * seq_len * batch


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## KV-cache arithmetic
    """)
    return


@app.cell
def _():
    seq_len = mo.ui.slider(512, 32_768, step=512, value=4096, label="context length (tokens)")
    batch = mo.ui.slider(1, 64, value=16, label="concurrent sequences")
    mo.hstack([seq_len, batch], gap=2, justify="start")
    return batch, seq_len


@app.cell
def _(batch, seq_len):
    _bytes = kv_cache_bytes(seq_len.value, batch.value)
    _per_seq = kv_cache_bytes(seq_len.value, 1)
    mo.hstack(
        [
            mo.stat(value=f"{_bytes / 1e9:.1f} GB", label="KV cache total", bordered=True),
            mo.stat(value=f"{_per_seq / 1e6:.0f} MB", label="per sequence", bordered=True),
            mo.stat(
                value=f"{_bytes / (14e9) * 100:.0f}%",
                label="vs 7B fp16 weights (~14 GB)",
                caption="the cache outgrows the model",
                bordered=True,
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    Llama-7B-ish geometry (32 layers · 8 KV heads · head_dim 128, fp16).
    Slide the context length: the cache scales **linearly with tokens and
    batch**, which is why naive per-request allocation fragments GPU memory
    — and why vLLM pages it.
    """)
    return


@app.function
def simulate_batching(n_requests: int = 64, batch_slots: int = 8, seed: int = 11) -> dict:
    """Compare static vs continuous batching on identical random workloads.

    Static: a batch of `batch_slots` runs until its LONGEST sequence
    finishes. Continuous: every finished slot is refilled next step.
    Returns total decode steps for each (same total tokens generated).
    """
    rng = random.Random(seed)
    lengths = [rng.randint(8, 256) for _ in range(n_requests)]
    # Static batching: ceil into groups; each group costs max(length) steps.
    static_steps = sum(max(lengths[i : i + batch_slots]) for i in range(0, n_requests, batch_slots))
    # Continuous batching: total work spread over always-full slots.
    continuous_steps = -(-sum(lengths) // batch_slots)  # ceil division
    return {
        "tokens": sum(lengths),
        "static_steps": static_steps,
        "continuous_steps": continuous_steps,
    }


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Continuous batching
    """)
    return


@app.cell
def _():
    sim = simulate_batching()
    _speedup = sim["static_steps"] / sim["continuous_steps"]
    mo.vstack(
        [
            mo.md(
                "**Continuous batching** on 64 simulated requests"
                " (8 slots, output lengths 8-256 tokens):"
            ),
            mo.hstack(
                [
                    mo.stat(
                        value=sim["static_steps"], label="static batching steps", bordered=True
                    ),
                    mo.stat(value=sim["continuous_steps"], label="continuous steps", bordered=True),
                    mo.stat(
                        value=f"{_speedup:.2f}x",
                        label="throughput gain",
                        caption="same tokens, fewer idle slots",
                        bordered=True,
                    ),
                ],
                gap=1,
            ),
        ],
        gap=0.5,
    )
    return (sim,)


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Paged attention in one paragraph": mo.md(
                """
    Naively, each sequence reserves a contiguous KV region sized for its
    *maximum* length — internal fragmentation, like pre-virtual-memory
    RAM. vLLM chops the cache into fixed **blocks** (~16 tokens) and keeps
    a per-sequence block table — literally the OS page-table trick. Result:
    near-zero waste, and beam-search branches can *share* prefix blocks
    copy-on-write.
    """
            ),
            "Promotion path (off-CI)": mo.md(
                """
    The real thing needs a GPU box: `uv add --script <this file> vllm`,
    then drive `vllm.LLM(...)` with these same sliders as sampling params.
    Keep it out of the CI smoke list per AGENTS.md CI-safety.
    """
            ),
            "TODO(you): the memory dial": mo.md(
                """
    Add a `block_size` slider and compute worst-case fragmentation for
    naive contiguous allocation vs paged blocks (hint: waste per sequence
    is `reserved - used` vs `block_size - (len % block_size)`). At what
    sequence-length variance does paging stop mattering?
    """
            ),
        }
    )
    return


@app.cell
def test_serving_arithmetic(sim):
    # KV cache scales linearly in both tokens and batch.
    assert kv_cache_bytes(2048, 4) == 2 * kv_cache_bytes(1024, 4)
    assert kv_cache_bytes(1024, 8) == 2 * kv_cache_bytes(1024, 4)
    # Continuous batching never loses to static on the same workload.
    assert sim["continuous_steps"] <= sim["static_steps"]
    # And the simulated gain is material on varied lengths.
    assert sim["static_steps"] / sim["continuous_steps"] > 1.3
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - E3: `ai_serving/fastapi/001_model_endpoint.py` — the API layer in
      front of any of this
    - E2 retrieval: `ml/faiss/001_ann_vector_search.py` already covers the
      vector half; embeddings join in the study-plan backlog
    """)
    return


if __name__ == "__main__":
    app.run()

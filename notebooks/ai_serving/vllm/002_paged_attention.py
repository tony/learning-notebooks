# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""vllm — paged attention, simulated: block-allocate the KV cache like virtual memory."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="serving: paged attention")


with app.setup:
    import random

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Paged attention: the KV cache as virtual memory (simulated, stdlib-only)

    `vllm/001` showed the KV cache *is* the memory problem. This notebook shows
    vLLM's answer. The naive engine reserves a **contiguous** slab of
    `max_seq_len` slots per request — but most requests stop early, so the slab
    sits mostly empty. **Paged attention** breaks the cache into fixed-size
    **blocks** drawn from a shared pool, allocated only as a sequence actually
    grows — exactly how an OS pages physical memory. The payoff is utilization,
    and utilization is concurrency. All arithmetic; no GPU.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/vllm-project/vllm>
    - In the source: `vllm/v1/core/block_pool.py` and `kv_cache_manager.py` (the
      allocator), `vllm/v1/core/single_type_kv_cache_manager.py` (blocks per
      sequence); the CUDA kernel is `csrc/attention/paged_attention_v1.cu`
    - Architecture corpus: the `vllm` study maps the block manager and scheduler.
    - Concepts: paged-attention, kv-cache, continuous-batching
    - See also: `notebooks/ai_serving/vllm/001_serving_concepts.py` — the KV-cache
      memory math this pages
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## A batch of variable-length requests

    Real serving traffic is short and uneven (chat turns, completions), but the
    engine must reserve for the worst case. 64 requests, each 8-128 tokens,
    against a `max_seq_len` of 512 — seeded so the numbers are stable.
    """)
    return


@app.cell
def _():
    block_size, max_seq_len, n_requests = 16, 512, 64
    _rng = random.Random(0)
    lengths = [_rng.randint(8, 128) for _ in range(n_requests)]
    used_tokens = sum(lengths)
    return block_size, lengths, max_seq_len, n_requests, used_tokens


@app.function
def blocks_for(length: int, block_size: int) -> int:
    """Number of fixed-size blocks a sequence of `length` tokens needs (ceil)."""
    return -(-length // block_size)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Contiguous vs paged, on the same batch

    Contiguous reserves `max_seq_len` per request no matter how short it turns
    out. Paged reserves `ceil(length / block_size)` blocks — its only waste is the
    partial last block of each sequence.
    """)
    return


@app.cell
def _(block_size, lengths, max_seq_len, n_requests, used_tokens):
    contiguous_slots = n_requests * max_seq_len
    paged_slots = sum(blocks_for(length, block_size) for length in lengths) * block_size
    summary = [
        {
            "scheme": "contiguous",
            "slots reserved": contiguous_slots,
            "tokens used": used_tokens,
            "utilization": f"{used_tokens / contiguous_slots:.0%}",
        },
        {
            "scheme": "paged",
            "slots reserved": paged_slots,
            "tokens used": used_tokens,
            "utilization": f"{used_tokens / paged_slots:.0%}",
        },
    ]
    mo.ui.table(summary, label="KV-cache utilization, identical traffic")
    return (paged_slots,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Utilization is concurrency

    The wasted slots aren't free — they're VRAM that could hold *another*
    request's cache. Below, a fixed pool of blocks (sized to hold the contiguous
    reservation of just 8 max-length sequences) is filled greedily with paged
    requests until it can't fit the next one. Paging admits many more — which is
    why continuous batching (refilling finished slots every step) has anything to
    refill *into*.
    """)
    return


@app.cell
def _(block_size, max_seq_len):
    pool = BlockAllocator((8 * max_seq_len) // block_size)
    contiguous_capacity = 8  # 8 sequences each reserving max_seq_len
    _stream = random.Random(1)
    admitted = 0
    while pool.allocate(blocks_for(_stream.randint(8, 128), block_size)):
        admitted += 1
    mo.md(
        f"""
    Same VRAM, two policies:

    - **contiguous** admits **{contiguous_capacity}** sequences (one max-length
      slab each), then blocks.
    - **paged** admits **{admitted}** — about **{admitted // contiguous_capacity}x**
      more — because each holds only the blocks it has actually filled.
    """
    )
    return


@app.class_definition
class BlockAllocator:
    """A pool of fixed-size KV-cache blocks, handed out on demand (vLLM-style).

    Tracks only counts — the real manager maps block ids to GPU slots and
    reference-counts shared prefixes — but the admission arithmetic is the same.
    """

    def __init__(self, total_blocks: int):
        self.total = total_blocks
        self.free = total_blocks

    def allocate(self, n_blocks: int) -> bool:
        """Reserve `n_blocks` if the pool can spare them; report success."""
        if n_blocks <= self.free:
            self.free -= n_blocks
            return True
        return False

    def release(self, n_blocks: int) -> None:
        """Return `n_blocks` to the pool (a sequence finished and freed its cache)."""
        self.free = min(self.total, self.free + n_blocks)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## TODO(you)

    Real block managers also **share** blocks: two requests with the same system
    prompt can point at one copy of its blocks (copy-on-write on divergence).
    Extend `BlockAllocator` with a `ref_count` per block and admit a batch that
    shares a 64-token prefix — how many more requests fit once the prefix is
    counted once instead of per request?
    """)
    return


@app.cell
def test_paging_beats_contiguous_and_the_pool_conserves_blocks():
    _rng = random.Random(0)
    _block_size, _max_seq_len = 16, 512
    _lengths = [_rng.randint(8, 128) for _ in range(64)]
    _used = sum(_lengths)
    _contiguous = 64 * _max_seq_len
    _paged = sum(blocks_for(length, _block_size) for length in _lengths) * _block_size
    # Paging wastes far less: same tokens, a fraction of the reservation.
    assert _paged < _contiguous
    assert _used / _paged > _used / _contiguous

    # The pool conserves blocks across allocate/release.
    _pool = BlockAllocator(10)
    assert _pool.allocate(7) and _pool.free == 3
    assert not _pool.allocate(4)  # only 3 left
    _pool.release(7)
    assert _pool.free == 10
    return


if __name__ == "__main__":
    app.run()

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "faiss-cpu",
#     "marimo",
#     "numpy",
# ]
# ///

"""faiss — quantization: trade memory for recall with IVF + product quantization."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="faiss: quantization")


with app.setup:
    import time

    import faiss
    import marimo as mo
    import numpy as np


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # faiss: trading memory for recall

    `faiss/001` traded *time* for recall (exact vs IVF, the `nprobe` dial). This
    notebook trades **memory**. A flat index stores every vector in full
    precision — 32 floats is 128 bytes each, and a billion vectors won't fit in
    RAM. **Product quantization** chops each vector into sub-vectors and replaces
    each with the id of a nearby centroid, so a vector becomes a handful of
    *bytes*. We measure the three-way tension every vector index lives in:
    **recall x latency x bytes-per-vector**.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/facebookresearch/faiss>
    - In the source: `faiss/IndexIVFPQ.cpp` (the combined index),
      `faiss/ProductQuantizer.cpp` (the encoder), `faiss/IndexIVFFlat.cpp`
      (full-precision IVF for the comparison)
    - Architecture corpus: the `faiss` study covers the index zoo and the
      quantizer training.
    - Concepts: quantization, approximate-nearest-neighbor, recall-speed-tradeoff, vectorized-execution
    - See also: `notebooks/ml/faiss/001_ann_vector_search.py` — exact vs IVF, the
      recall/speed dial this picks up from
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## A synthetic vector set

    4000 base vectors and 200 queries in 32 dimensions, seeded so every run (and
    the test cell) sees the same data. faiss wants `float32`, C-contiguous.
    """)
    return


@app.cell
def _():
    _rng = np.random.default_rng(0)
    dim = 32
    base = _rng.standard_normal((4000, dim), dtype=np.float32)
    queries = _rng.standard_normal((200, dim), dtype=np.float32)
    k = 10
    return base, dim, k, queries


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## The exact baseline

    `IndexFlatL2` is brute force: it stores every vector and compares the query
    against all of them. Its results *are* the ground truth — recall is 1.0 by
    definition — and its memory is the full `dim x 4` bytes per vector.
    """)
    return


@app.cell
def _(base, dim, k, queries):
    flat = faiss.IndexFlatL2(dim)
    flat.add(base)
    _t = time.perf_counter()
    _, truth = flat.search(queries, k)
    flat_ms = (time.perf_counter() - _t) * 1000
    flat_bytes = dim * 4
    return flat_bytes, flat_ms, truth


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## IVF, then IVF + product quantization

    `IndexIVFFlat` keeps full precision but only scans `nprobe` of `nlist`
    cells. `IndexIVFPQ` adds the quantizer: each 32-d vector is split into
    `m = 8` sub-vectors of 4 dims, and each sub-vector is replaced by one of
    `2**nbits = 16` learned centroids — so the stored code is `m x nbits / 8 = 4`
    bytes, a 32x shrink. Both must be **trained** (k-means) before they accept
    data.
    """)
    return


@app.cell
def _(base, dim, k, queries):
    nlist, nprobe, m, nbits = 32, 8, 8, 4
    _quant = faiss.IndexFlatL2(dim)

    ivf = faiss.IndexIVFFlat(_quant, dim, nlist)
    ivf.train(base)
    ivf.add(base)
    ivf.nprobe = nprobe

    ivfpq = faiss.IndexIVFPQ(faiss.IndexFlatL2(dim), dim, nlist, m, nbits)
    ivfpq.train(base)
    ivfpq.add(base)
    ivfpq.nprobe = nprobe

    pq_bytes = m * nbits // 8
    return ivf, ivfpq, pq_bytes


@app.function
def measure(index, queries, truth, bytes_per_vec):
    """Search `queries`, returning (recall@k vs `truth`, batch latency ms, bytes/vec)."""
    start = time.perf_counter()
    _, found = index.search(queries, truth.shape[1])
    elapsed_ms = (time.perf_counter() - start) * 1000
    hits = sum(len(set(f) & set(t)) for f, t in zip(found, truth, strict=True))
    recall = hits / truth.size
    return recall, elapsed_ms, bytes_per_vec


@app.cell
def _(flat_bytes, flat_ms, ivf, ivfpq, pq_bytes, queries, truth):
    rows = [
        {
            "index": "Flat (exact)",
            "recall@10": 1.0,
            "query ms": round(flat_ms, 2),
            "bytes/vec": flat_bytes,
        },
    ]
    for _name, _idx, _bytes in [("IVFFlat", ivf, flat_bytes), ("IVFPQ", ivfpq, pq_bytes)]:
        _recall, _ms, _b = measure(_idx, queries, truth, _bytes)
        rows.append(
            {
                "index": _name,
                "recall@10": round(_recall, 3),
                "query ms": round(_ms, 2),
                "bytes/vec": _b,
            }
        )
    mo.ui.table(rows, label="recall x latency x memory, same 200 queries")
    return (rows,)


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Reading the tradeoff

    Three dials, three costs:

    - **`nprobe`** (how many cells to scan) buys recall with latency — the
      `faiss/001` dial, still here.
    - **`m` and `nbits`** (how finely to quantize) buy recall with *memory*. More
      sub-quantizers or more centroids per sub-quantizer mean a longer code and a
      better approximation.

    IVFPQ gives up some recall, but the `bytes/vec` column is the headline: a 32x
    smaller index is the difference between fitting in RAM and not. At billion
    scale that is the only question that matters, which is why production vector
    search is almost always quantized.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## TODO(you)

    Raise `nbits` from 4 to 8 (256 centroids per sub-quantizer). Predict the
    effect on each column before you re-run: recall should climb, `bytes/vec`
    should double to 8, and training will take longer. Which moved most?
    """)
    return


@app.cell
def test_quantization_shrinks_memory_and_keeps_useful_recall():
    _rng = np.random.default_rng(0)
    _dim, _k = 32, 10
    _base = _rng.standard_normal((4000, _dim), dtype=np.float32)
    _queries = _rng.standard_normal((200, _dim), dtype=np.float32)

    _flat = faiss.IndexFlatL2(_dim)
    _flat.add(_base)
    _, _truth = _flat.search(_queries, _k)

    _pq = faiss.IndexIVFPQ(faiss.IndexFlatL2(_dim), _dim, 32, 8, 4)
    _pq.train(_base)
    _pq.add(_base)
    _pq.nprobe = 8
    _recall, _ms, _bytes = measure(_pq, _queries, _truth, 8 * 4 // 8)

    assert _bytes < _dim * 4  # quantization compressed the vector (4 vs 128 bytes)
    assert 0.0 < _recall <= 1.0  # approximate, but it finds real neighbours
    return


if __name__ == "__main__":
    app.run()

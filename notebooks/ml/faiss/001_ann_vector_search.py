# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "faiss-cpu",
#     "marimo",
#     "numpy",
# ]
# ///

"""faiss — ANN vector search: exact vs IVF, the recall/speed dial."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="faiss: ANN vector search")


with app.setup:
    import time

    import faiss
    import marimo as mo
    import numpy as np


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Approximate nearest neighbors: trading recall for speed

    Exact search compares a query against **every** vector; IVF first asks a
    coarse quantizer *which cells could contain the answer* and scans only
    those inverted lists — the same posting-list idea as text search, with
    centroids instead of terms. `nprobe` is the dial: more cells, more
    recall, more time.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/facebookresearch/faiss>
    - In the source: `faiss/IndexFlat.cpp`
      (brute force) vs `faiss/IndexIVFFlat.cpp` (inverted lists);
      `faiss/Clustering.cpp` trains the coarse quantizer
    - Architecture corpus: the `faiss` study (115 files).
    """)
    return


@app.cell
def _():
    rng = np.random.default_rng(7)
    dim, n_db, n_clusters = 64, 20_000, 16
    _centers = rng.normal(size=(n_clusters, dim)).astype(np.float32) * 5
    _assign = rng.integers(0, n_clusters, size=n_db)
    database = (_centers[_assign] + rng.normal(size=(n_db, dim)).astype(np.float32)).astype(
        np.float32
    )
    # Queries are perturbed copies of known database rows — planted neighbors.
    query_ids = np.arange(0, n_db, n_db // 100, dtype=np.int64)[:100]
    queries = database[query_ids] + rng.normal(scale=0.01, size=(100, dim)).astype(np.float32)
    return database, dim, queries, query_ids


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The exact baseline
    """)
    return


@app.cell
def _(database, dim, queries):
    flat = faiss.IndexFlatL2(dim)
    flat.add(database)
    _t0 = time.perf_counter()
    _dists, flat_ids = flat.search(queries, 10)
    flat_ms = (time.perf_counter() - _t0) * 1000
    return flat_ids, flat_ms


@app.cell
def _():
    nprobe = mo.ui.slider(1, 128, value=8, label="nprobe (IVF cells probed per query)")
    nprobe
    return (nprobe,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## IVF and the nprobe dial
    """)
    return


@app.cell
def _(database, dim, flat_ids, flat_ms, nprobe, queries):
    quantizer = faiss.IndexFlatL2(dim)
    ivf = faiss.IndexIVFFlat(quantizer, dim, 128)
    ivf.train(database)
    ivf.add(database)
    ivf.nprobe = nprobe.value
    _t0 = time.perf_counter()
    _dists, ivf_ids = ivf.search(queries, 10)
    ivf_ms = (time.perf_counter() - _t0) * 1000
    recall = float(
        np.mean([len(set(f) & set(a)) / 10 for f, a in zip(flat_ids, ivf_ids, strict=True)])
    )
    mo.hstack(
        [
            mo.stat(value=f"{recall:.1%}", label="recall@10 vs exact", bordered=True),
            mo.stat(value=f"{flat_ms:.1f} ms", label="exact (scan all 20k)", bordered=True),
            mo.stat(
                value=f"{ivf_ms:.1f} ms",
                label=f"IVF @ nprobe={nprobe.value}",
                caption=f"{flat_ms / max(ivf_ms, 1e-9):.1f}x faster",
                bordered=True,
            ),
        ],
        gap=1,
    )
    return (ivf,)


@app.cell(hide_code=True)
def _(nprobe):
    mo.callout(
        mo.md(
            f"Slide `nprobe` and watch the dial: at `{nprobe.value}` of 128"
            " cells you're scanning roughly"
            f" **{nprobe.value / 128:.0%}** of the inverted lists. Recall"
            " climbs steeply at first — most true neighbors live in the"
            " query's own cell or its immediate rivals."
        ),
        kind="info",
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "IVF is an inverted index for geometry": mo.md(
                """
    Train k-means on the corpus → 128 centroids. Each database vector is
    filed under its nearest centroid (an **inverted list**, exactly the
    posting-list shape from BM25 search — centroid where text search has
    a term). A query embeds, finds its `nprobe` nearest centroids, and
    scans only those lists. HNSW replaces the cell structure with a
    navigable small-world graph; PQ compresses the vectors inside lists.
    """
            ),
            "TODO(you): the nlist tradeoff": mo.md(
                """
    Rebuild with `nlist=16` and `nlist=512` (retrain each time). For a
    fixed `nprobe/nlist` *fraction*, which gives better recall-per-ms on
    this clustered data — and why does the answer change if the data has
    no cluster structure at all (try pure `rng.normal` vectors)?
    """
            ),
        }
    )
    return


@app.cell
def test_ann(database, flat_ids, ivf, queries, query_ids):
    # Exact search finds every planted neighbor at rank 0.
    assert (flat_ids[:, 0] == query_ids).all()
    # Probing ALL cells makes IVF exhaustive — identical to exact search.
    ivf.nprobe = 128
    _, _all_ids = ivf.search(queries, 10)
    _recall = np.mean([len(set(f) & set(a)) / 10 for f, a in zip(flat_ids, _all_ids, strict=True)])
    assert _recall == 1.0, _recall
    assert ivf.ntotal == database.shape[0]
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - C3 upstream: real embeddings (sentence-transformers — model download,
      so it stays out of CI; see `notes/study_plan.md` backlog)
    - The retrieval half of RAG (taxonomy E2) is exactly this notebook plus
      an embedding model in front
    """)
    return


if __name__ == "__main__":
    app.run()

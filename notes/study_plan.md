# Study Plan

A living document: which libraries to study, in what order, and where their
sources live. Clones are siblings of this repo (`../<clone dir>`).

## Tracks

### Track 1 — Data stack (start here; light deps, instant sandboxes)

| Topic dir | Clone | Upstream | Focus |
| --- | --- | --- | --- |
| `pandas/` | `../pandas` | <https://github.com/pandas-dev/pandas> | indexing, dtypes, groupby internals |
| `numpy/` | `../numpy` | <https://github.com/numpy/numpy> | broadcasting, strides, ufuncs |
| `matplotlib/` | `../matplotlib` | <https://github.com/matplotlib/matplotlib> | figure/axes model, artists |
| `plotnine/` | `../plotnine` | <https://github.com/has2k1/plotnine> | grammar of graphics on matplotlib |
| `rich/` | `../rich` | <https://github.com/Textualize/rich> | console protocol, renderables |
| `pydantic/` | `../pydantic` | <https://github.com/pydantic/pydantic> | validation core, type adapters |

### Track 2 — SQL & dataframes (marimo's `mo.sql()` shines here)

| Topic dir | Clone | Upstream | Focus |
| --- | --- | --- | --- |
| `ibis/` | `../ibis` | <https://github.com/ibis-project/ibis> | expression IR, duckdb backend |
| `dask/` | `../dask` | <https://github.com/dask/dask> | task graphs, lazy collections |
| `modin/` | `../modin` | <https://github.com/modin-project/modin> | pandas API on parallel engines |

### Track 3 — Statistics & ML (medium deps)

| Topic dir | Clone | Upstream | Focus |
| --- | --- | --- | --- |
| `scikit-learn/` | `../scikit-learn` | <https://github.com/scikit-learn/scikit-learn> | estimator API, pipelines |
| `statsmodels/` | `../statsmodels` | <https://github.com/statsmodels/statsmodels> | formula API, results objects |
| `scipy/` | `../scipy` | <https://github.com/scipy/scipy> | optimize, sparse, stats |

### Track 4 — Deep learning (heavy deps; never in CI; use `@mo.persistent_cache`)

| Topic dir | Clone | Upstream | Focus |
| --- | --- | --- | --- |
| `torch/` | `../pytorch` | <https://github.com/pytorch/pytorch> | tensors, autograd, modules |
| `transformers/` | `../transformers` | <https://github.com/huggingface/transformers> | pipelines, tokenizers, model loading |
| `datasets/` | `../datasets` | <https://github.com/huggingface/datasets> | arrow-backed datasets, streaming |
| `sentence-transformers/` | `../sentence-transformers` | <https://github.com/UKPLab/sentence-transformers> | embeddings, similarity |
| `diffusers/` | `../diffusers` | <https://github.com/huggingface/diffusers> | pipelines, schedulers |

### Track 5 — The notebook itself

| Topic dir | Clone | Upstream | Focus |
| --- | --- | --- | --- |
| `marimo/` | `../marimo` | <https://github.com/marimo-team/marimo> | reactivity/DAG, codegen, sandbox |

## Conventions

- Note: the topic dir is the *import name* where it differs from the clone dir
  (e.g. `torch/` studies the clone at `../pytorch`).
- Add new rows as new libraries enter the rotation; reorder tracks freely.

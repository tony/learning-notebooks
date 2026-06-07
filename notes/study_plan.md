# Study Plan

A living document: the forward roadmap for filling `notes/taxonomy.md`, ordered by
the **mastery ladder** (L1 fundamentals → L2 self-sufficiency → L3 reproducible &
synergy → L4 enterprise). Clones live as siblings of this repo's parent
(`../<repo>` or `../../<lang>/<repo>` relative to this repo).

## Current wave — complete the ladder

| Notebook | Track · Rung | Deps | Teaches |
|---|---|---|---|
| `systems/cpython/001_bytecode_dis.py` | A1 · L1 | marimo | `dis`, code objects, the stack machine |
| `data/pyarrow/002_zero_copy_synergy.py` | B3/B4 · L3 | +pandas, polars, duckdb | one Arrow table, three engines, zero copies |
| `ml/tokenizers/001_bpe_from_scratch.py` | C3 · L1 | +tokenizers | BPE merges by hand vs the Rust library |
| `ml/faiss/001_ann_vector_search.py` | C3 · L2 | +faiss-cpu, numpy | exact vs IVF ANN; recall/speed tradeoff |
| `ai_serving/vllm/001_serving_concepts.py` | E1 · L1 | marimo | KV-cache memory + batching, simulated |
| `ai_serving/fastapi/001_model_endpoint.py` | E3 · L2 | +fastapi | model endpoint exercised via TestClient |
| `enterprise/kafka/001_event_patterns.py` | F1 · L4 | marimo | outbox + idempotent consumer, no broker |
| `enterprise/airflow/001_dag_from_scratch.py` | F2 · L1 | marimo | a scheduler on `graphlib`; retries, idempotency |
| `enterprise/locust/001_load_modeling.py` | F3 · L4 | marimo | percentiles, Little's law, saturation |
| `enterprise/presidio/001_pii_governance.py` | F4 · L4 | marimo | PII scanning, redaction, audit hashing |

## Backlog (rows that stay `needs notebook` / `seed` after this wave)

- **L1**: micrograd-style autograd (promote `ml/torch/001` from md-first);
  B-tree/page layout walk (`../../c/sqlite` `src/btree.c`)
- **L2**: matplotlib (figure/axes model), plotnine, pydantic (validation core),
  dask (task graphs), modin, statsmodels, scipy.optimize, datasets, qdrant/chroma
- **L3**: ibis-to-many-backends (same expression, duckdb vs polars); a
  cross-notebook pipeline (pyarrow → duckdb → sklearn) with `mo.persistent_cache`;
  notebook-as-module reuse across the repo
- **L4**: opentelemetry tracing of the fastapi endpoint; delta-rs ACID tables;
  real locust run against a served notebook; presidio promotion (spacy models —
  heavy, never in CI)
- **Heavy track** (lives in `../learning-ai-tuning`): D2 PEFT/LoRA, D3 alignment

## Conventions

- Topic dir = import name where it differs from the clone dir (`torch/` studies
  `../pytorch`; `cpython/` studies `../../c/cpython`).
- Add rows as libraries enter the rotation; flip taxonomy statuses as artifacts
  land; heavy deps never join the CI smoke list (`AGENTS.md` CI-safety).

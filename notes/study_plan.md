# Study Plan

A living document: the forward roadmap for filling `notes/taxonomy.md`, ordered by
the **mastery ladder** (fundamentals → self-sufficiency → reproducible → production).

## Current wave — complete the ladder

| Notebook | Track · Rung | Deps | Teaches |
|---|---|---|---|
| `systems/cpython/001_bytecode_dis.py` | systems/languages-runtimes · fundamentals | marimo | `dis`, code objects, the stack machine |
| `data/pyarrow/002_zero_copy_synergy.py` | data/distributed · reproducible | +pandas, polars, duckdb | one Arrow table, three engines, zero copies |
| `ml/tokenizers/001_bpe_from_scratch.py` | ml/nlp-embeddings · fundamentals | +tokenizers | BPE merges by hand vs the Rust library |
| `ml/faiss/001_ann_vector_search.py` | ml/nlp-embeddings · self-sufficiency | +faiss-cpu, numpy | exact vs IVF ANN; recall/speed tradeoff |
| `ai_serving/vllm/001_serving_concepts.py` | ai-serving/inference · fundamentals | marimo | KV-cache memory + batching, simulated |
| `ai_serving/fastapi/001_model_endpoint.py` | ai-serving/observability · self-sufficiency | +fastapi | model endpoint exercised via TestClient |
| `enterprise/kafka/001_event_patterns.py` | enterprise/messaging · production | marimo | outbox + idempotent consumer, no broker |
| `enterprise/airflow/001_dag_from_scratch.py` | enterprise/orchestration · fundamentals | marimo | a scheduler on `graphlib`; retries, idempotency |
| `enterprise/locust/001_load_modeling.py` | enterprise/reliability · production | marimo | percentiles, Little's law, saturation |
| `enterprise/presidio/001_pii_governance.py` | enterprise/governance · production | marimo | PII scanning, redaction, audit hashing |

## Backlog (rows that stay `needs notebook` / `seed` after this wave)

- **fundamentals**: micrograd-style autograd (promote `ml/torch/001` from
  md-first); a B-tree/page layout walk (sqlite `src/btree.c`)
- **self-sufficiency**: matplotlib (figure/axes model), plotnine, pydantic
  (validation core), dask (task graphs), modin, statsmodels, scipy.optimize,
  datasets, qdrant/chroma
- **reproducible**: ibis-to-many-backends (same expression, duckdb vs polars); a
  cross-notebook pipeline (pyarrow → duckdb → sklearn) with `mo.persistent_cache`;
  notebook-as-module reuse across the repo
- **production**: opentelemetry tracing of the fastapi endpoint; delta-rs ACID
  tables; a real locust run against a served notebook; presidio promotion (spacy
  models — heavy, never in CI)
- **Rust in Python** (`systems/rust-in-python`): pyo3 native modules, a maturin
  wheel build, the polars rust-core/python-frontend loop, a CLI shipped as a
  wheel (ruff/uv/ty)
- **Heavy track** (lives in `../learning-ai-tuning`): PEFT/LoRA, then alignment

## Conventions

- The notebook library directory names the project; the upstream is in the
  source-reading cell. Where a clone lives locally is per-machine (resolved at
  runtime via `$STUDY_ROOT` / vcspull), never authored here.
- Add rows as libraries enter the rotation; flip taxonomy statuses as artifacts
  land; heavy deps never join the CI smoke list (`AGENTS.md` CI-safety).

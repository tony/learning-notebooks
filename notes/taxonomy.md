# Learning Taxonomy Index

The bridge between the two study corpora:

1. **Curriculum mode** — `learning-*` sibling repos with `notes/` progressions and
   marimo notebooks (PEP 723, `uv --sandbox`). This repo's rules: `AGENTS.md`.
2. **Architecture-study mode** — deep source reads under the work-notes corpus,
   referenced below as `architecture/<project>/` (146 project dirs at last count).

Each row indexes one taxonomy track. Notebooks for **any** domain are born in this
repo under `notebooks/<domain>/<library>/`; sibling `learning-<track>` repos are
optional — a track graduates only if it outgrows this repo (as `learning-ai-tuning`
did for D1).

**Mastery ladder** (orthogonal to domains — the rung a row's current artifact teaches):

- **L1 fundamentals** — build the concept from first principles, stdlib-first
- **L2 self-sufficiency** — drive the real library competently
- **L3 reproducible & synergy** — compose tools; interop, caching, tests as one system
- **L4 enterprise** — org-scale patterns: orchestration, messaging, load, governance

**License policy:** notebook PEP 723 dependencies must be permissive
(MIT/BSD/Apache-2.0/PSF/ISC). MPL-2.0 is dev/test-only and flagged `⚑`.
GPL/AGPL/SSPL/BUSL/RSAL targets are *study-only* — read in architecture mode,
never a dependency. License unclear → `study-only` until verified.

**Statuses:** `existing` · `seed` (entry-point notebook exists; depth pending) ·
`needs notebook` · `needs architecture link` · `needs license verification` ·
`study-only` · `deferred`

| Domain | Track | Topic | Notebook | Architecture study | Packages | License status | Mastery | Status |
|---|---|---|---|---|---|---|---|---|
| 0 | Toolchain | Reproducible study notebooks | [notebooks/toolchain/marimo/001_basics.py](../notebooks/toolchain/marimo/001_basics.py) | `architecture/{marimo,uv,ruff,pytest}` | marimo, uv, ruff, ty, pytest, rich | permissive (Apache-2.0 / MIT) | L2 | existing |
| A | A1 | Languages & runtimes (bytecode → GC → JIT → types) | [cpython dis seed](../notebooks/systems/cpython/001_bytecode_dis.py) | `architecture/{cpython,ty,cython,v8,node,rust,pyo3,maturin}` | CPython [PSF], ty [MIT], cython [Apache-2.0], V8 [BSD], Node [MIT], Rust [MIT/Apache-2.0], pyo3/maturin [Apache-2.0] | permissive | L1 | seed |
| A | A2 | Data structures & algorithms | [sortedcontainers seed](../notebooks/systems/sortedcontainers/001_ordered_structures.py) · ✎ `../learning-dsa/notes/progression-algo.md` | `architecture/{cpython}` | sortedcontainers [Apache-2.0], networkx [BSD], hypothesis [MPL-2.0 ⚑] | permissive + ⚑ hypothesis (dev/test only) | L2 | existing |
| A | A3 | Concurrency & async (event loop → futures → actors) | [anyio seed](../notebooks/systems/anyio/001_structured_concurrency.py) · ✎ `../learning-asyncio/notes/progression.md` | `architecture/{cpython-asyncio,tokio,libuv,libevent,futures-rs,rayon}` | anyio [MIT], trio [MIT/Apache-2.0], Tokio [MIT], rayon [MIT/Apache-2.0] | permissive | L2 | existing |
| A | A4 | OS / kernels / systems | — | `architecture/{linux,freebsd,openbsd,fuchsia,reactos,haiku,sqlite,osquery}` | study targets only — Linux [GPL], FreeBSD/OpenBSD [BSD], SQLite [public domain] | GPL targets never become deps | — | study-only |
| A | A5 | Build & dev tooling (packaging → linters → tests → terminals) | [notebooks/systems/rich/001_console_rendering.py](../notebooks/systems/rich/001_console_rendering.py) · ✎ `../learning-pytest-internals/notes/progression.md` | `architecture/{uv,ruff,pytest,bazel,cmake,nix,rich,textual,tmux,setuptools}` | uv [MIT/Apache-2.0], ruff [MIT], pytest [MIT], rich/textual [MIT], setuptools [MIT] | permissive | L2 | existing |
| B | B1 | Numeric & dataframe core (ndarray → dataframe → plotting → validation) | [notebooks/data/pandas/001_dataframes.py](../notebooks/data/pandas/001_dataframes.py) · [numpy seed](../notebooks/data/numpy/001_broadcasting_strides.py) · [polars seed](../notebooks/data/polars/001_lazy_frames.py) | `architecture/{numpy,pandas,polars,rich}` (missing: matplotlib, plotnine, pydantic) | numpy [BSD], pandas [BSD], polars [MIT], matplotlib [PSF-based], plotnine [MIT], pydantic [MIT] | permissive | L1–L2 | existing |
| B | B2 | SQL & query engines (expression IR → plans → vectorized exec) | [notebooks/data/ibis/001_duckdb_sql.py](../notebooks/data/ibis/001_duckdb_sql.py) · [duckdb seed](../notebooks/data/duckdb/001_vectorized_exec.py) | `architecture/{duckdb,datafusion,dask,sqlalchemy,clickhouse}` (missing: ibis, modin) | ibis [Apache-2.0], duckdb [MIT], datafusion [Apache-2.0], sqlalchemy [MIT], dask [BSD], modin [Apache-2.0] | permissive | L2 | existing |
| B | B3 | Distributed data & streaming — analytics (task graphs → shuffle → exactly-once) | [pyarrow seed](../notebooks/data/pyarrow/001_columnar_memory.py) | `architecture/{arrow,spark,flink,kafka,ray,daft,pulsar,hadoop,pig}` | pyarrow, Spark, Flink, Kafka, Ray, Daft, Pulsar [all Apache-2.0] | permissive | L2 | seed |
| B | B4 | Storage & lakehouse formats (columnar → ACID tables) | [pyarrow seed](../notebooks/data/pyarrow/001_columnar_memory.py) | `architecture/{arrow,delta-rs,delta-kernel-rs,clickhouse,opensearch}` | Arrow, delta-rs, ClickHouse, OpenSearch [all Apache-2.0] | permissive | L2 | seed |
| C | C1 | Classical ML & stats (regression → estimators → CV) | [sklearn seed](../notebooks/ml/sklearn/001_estimator_api.py) | `architecture/{scikit-learn,scipy}` (missing: statsmodels) | scikit-learn [BSD], scipy [BSD], statsmodels [BSD] | permissive | L2 | seed |
| C | C2 | Deep learning core (tensors/autograd → training loop → tiny-GPT) | [torch seed](../notebooks/ml/torch/001_autograd.py) (md-first — torch not CI-executed) | `architecture/{pytorch,candle,tensorflow,onnx}` | torch [BSD], candle [MIT/Apache-2.0], micrograd/nanoGPT [MIT], onnx [Apache-2.0] | permissive | L1 | seed |
| C | C3 | NLP / embeddings / vector search (tokenization → ANN → vector DB) | [BPE-scratch seed](../notebooks/ml/tokenizers/001_bpe_from_scratch.py) · [faiss ANN seed](../notebooks/ml/faiss/001_ann_vector_search.py) | `architecture/{sentence-transformers,faiss,chroma}` (missing: transformers, tokenizers) | tokenizers/tiktoken [Apache-2.0/MIT], sentence-transformers [Apache-2.0], faiss [MIT], chroma [Apache-2.0], qdrant [Apache-2.0] | permissive | L1–L2 | seed |
| D | D1 | Data & eval harness (metrics → gates → run store → search) | ✎ `../learning-ai-tuning/notebooks/eval/` (001–006: harness, sqlite store, FTS5, duckdb, BM25-scratch, tantivy) | `architecture/{axolotl,accelerate,optimum,sqlite,tantivy,lucene}` | scikit-learn [BSD], stdlib json/sqlite3 [PSF], duckdb [MIT], tantivy [MIT] | permissive | L1–L3 | existing |
| E | E1 | Inference & serving (KV-cache → batching → paged attention) | [serving-sim seed](../notebooks/ai_serving/vllm/001_serving_concepts.py) | `architecture/{vllm,ollama,optimum,onnx}` | vllm [Apache-2.0], ollama [MIT], llama.cpp [MIT], candle [MIT/Apache-2.0] | permissive | L1 | seed |
| E | E2 | RAG & agents (retrieval → structured output → multi-agent) | ✎ `../learning-ai/notes/lesson_plan.md` (Tiers 10–18) | `architecture/{llama_index,langchain,langgraph,deepagents,chroma,faiss}` | llama_index [MIT], langchain/langgraph [MIT], outlines [Apache-2.0], instructor [MIT] | permissive | L2 | seed |
| E | E3 | Productionizing & observability (API → tracing → cost) | — | (missing: fastapi) | fastapi [MIT], litestar [MIT], opentelemetry [Apache-2.0], pydantic [MIT] | permissive | L2 | needs notebook |
| F | F1 | Integration & messaging — operational (outbox → pub/sub → CDC) | — | `architecture/{kafka,pulsar,sqlalchemy}` | Kafka [Apache-2.0], Pulsar [Apache-2.0], stdlib sqlite3 [PSF] | permissive | L4 | needs notebook |
| F | F2 | Workflow & orchestration (DAGs → retries → idempotency) | — | `architecture/{airflow,dask,ray}` | airflow [Apache-2.0], prefect [Apache-2.0], stdlib graphlib [PSF] | permissive | L1 | needs notebook |
| F | F3 | Reliability, load & performance (load models → percentiles → SLOs) | — | `architecture/{locust,jmeter,vegeta,hyperfine}` | locust [MIT], hyperfine [MIT/Apache-2.0], stdlib random/statistics [PSF] | permissive | L4 | needs notebook |
| F | F4 | Security, privacy & governance (PII → redaction → audit) | — | `architecture/{presidio,opensearch}` | presidio [MIT], stdlib re/hashlib [PSF] | permissive | L4 | needs notebook |

Notes:

- `✎` marks a curriculum living in a sibling `learning-*` repo (relative paths from
  this repo's root). `architecture/<project>/` paths are all **verified present** in
  the corpus; gaps are listed inline as `missing:` and imply
  `needs architecture link` for those specific packages.
- The roadmap that fills the `needs notebook` rows lives in `notes/study_plan.md`,
  ordered by mastery rung.
- D/E/F build order (from the taxonomy artifact): D1 first ("you can't tune what
  you can't measure") — satisfied by `../learning-ai-tuning/`; E and F notebooks
  are born here under `notebooks/ai_serving/` and `notebooks/enterprise/`.

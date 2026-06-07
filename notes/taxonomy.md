# Learning Taxonomy Index

The bridge between the two study corpora:

1. **Curriculum mode** — `learning-*` sibling repos with `notes/` progressions and
   marimo notebooks (PEP 723, `uv --sandbox`). This repo's rules: `AGENTS.md`.
2. **Architecture-study mode** — deep source reads under the work-notes corpus,
   referenced below as `architecture/<project>/` (146 project dirs at last count).

Each row indexes one taxonomy track: domains A–C (mature) plus the Layer-0 study
toolchain. Domains D (AI tuning), E (AI usage/deployment), and F (enterprise
architecture) are the deliberate build-out — rows land here only when their first
artifact exists (source: the woven taxonomy artifact, 2026-06-07).

Notebooks for **any** domain are born in this repo under
`notebooks/<domain>/<library>/`; sibling `learning-<track>` repos are optional —
a track graduates only if it outgrows this repo (as `learning-ai-tuning` did
for D1).

**License policy:** notebook PEP 723 dependencies must be permissive
(MIT/BSD/Apache-2.0/PSF/ISC). MPL-2.0 is dev/test-only and flagged `⚑`.
GPL/AGPL/SSPL/BUSL/RSAL targets are *study-only* — read in architecture mode,
never a dependency. License unclear → `study-only` until verified.

**Statuses:** `existing` · `seed` (entry-point notebook exists; depth pending) ·
`needs notebook` · `needs architecture link` · `needs license verification` ·
`study-only` · `deferred`

| Domain | Track | Topic | Notebook | Architecture study | Packages | License status | Status |
|---|---|---|---|---|---|---|---|
| 0 | Toolchain | Reproducible study notebooks | [notebooks/toolchain/marimo/001_basics.py](../notebooks/toolchain/marimo/001_basics.py) | `architecture/{marimo,uv,ruff,pytest}` | marimo, uv, ruff, ty, pytest, rich | permissive (Apache-2.0 / MIT) | existing |
| A | A1 | Languages & runtimes (bytecode → GC → JIT → types) | — | `architecture/{cpython,ty,cython,v8,node,rust,pyo3,maturin}` | CPython [PSF], ty [MIT], cython [Apache-2.0], V8 [BSD], Node [MIT], Rust [MIT/Apache-2.0], pyo3/maturin [Apache-2.0] | permissive | needs notebook |
| A | A2 | Data structures & algorithms | ✎ `../learning-dsa/notes/progression-algo.md` | `architecture/{cpython}` | sortedcontainers [Apache-2.0], networkx [BSD], hypothesis [MPL-2.0 ⚑] | permissive + ⚑ hypothesis (dev/test only) | existing |
| A | A3 | Concurrency & async (event loop → futures → actors) | ✎ `../learning-asyncio/notes/progression.md` | `architecture/{cpython-asyncio,tokio,libuv,libevent,futures-rs,rayon}` | anyio [MIT], trio [MIT/Apache-2.0], Tokio [MIT], rayon [MIT/Apache-2.0] | permissive | existing |
| A | A4 | OS / kernels / systems | — | `architecture/{linux,freebsd,openbsd,fuchsia,reactos,haiku,sqlite,osquery}` | study targets only — Linux [GPL], FreeBSD/OpenBSD [BSD], SQLite [public domain] | GPL targets never become deps | study-only |
| A | A5 | Build & dev tooling (packaging → linters → tests → terminals) | [notebooks/systems/rich/001_console_rendering.py](../notebooks/systems/rich/001_console_rendering.py) · ✎ `../learning-pytest-internals/notes/progression.md` | `architecture/{uv,ruff,pytest,bazel,cmake,nix,rich,textual,tmux,setuptools}` | uv [MIT/Apache-2.0], ruff [MIT], pytest [MIT], rich/textual [MIT], setuptools [MIT] | permissive | existing |
| B | B1 | Numeric & dataframe core (ndarray → dataframe → plotting → validation) | [notebooks/data/pandas/001_dataframes.py](../notebooks/data/pandas/001_dataframes.py) · [numpy seed](../notebooks/data/numpy/001_broadcasting_strides.py) · [polars seed](../notebooks/data/polars/001_lazy_frames.py) | `architecture/{numpy,pandas,polars,rich}` (missing: matplotlib, plotnine, pydantic) | numpy [BSD], pandas [BSD], polars [MIT], matplotlib [PSF-based], plotnine [MIT], pydantic [MIT] | permissive | existing |
| B | B2 | SQL & query engines (expression IR → plans → vectorized exec) | [notebooks/data/ibis/001_duckdb_sql.py](../notebooks/data/ibis/001_duckdb_sql.py) · [duckdb seed](../notebooks/data/duckdb/001_vectorized_exec.py) | `architecture/{duckdb,datafusion,dask,sqlalchemy,clickhouse}` (missing: ibis, modin) | ibis [Apache-2.0], duckdb [MIT], datafusion [Apache-2.0], sqlalchemy [MIT], dask [BSD], modin [Apache-2.0] | permissive | existing |
| B | B3 | Distributed data & streaming — analytics (task graphs → shuffle → exactly-once) | [pyarrow seed](../notebooks/data/pyarrow/001_columnar_memory.py) | `architecture/{arrow,spark,flink,kafka,ray,daft,pulsar,hadoop,pig}` | pyarrow, Spark, Flink, Kafka, Ray, Daft, Pulsar [all Apache-2.0] | permissive | seed |
| B | B4 | Storage & lakehouse formats (columnar → ACID tables) | [pyarrow seed](../notebooks/data/pyarrow/001_columnar_memory.py) | `architecture/{arrow,delta-rs,delta-kernel-rs,clickhouse,opensearch}` | Arrow, delta-rs, ClickHouse, OpenSearch [all Apache-2.0] | permissive | seed |
| C | C1 | Classical ML & stats (regression → estimators → CV) | — | `architecture/{scikit-learn,scipy}` (missing: statsmodels) | scikit-learn [BSD], scipy [BSD], statsmodels [BSD] | permissive | needs notebook |
| C | C2 | Deep learning core (tensors/autograd → training loop → tiny-GPT) | — | `architecture/{pytorch,candle,tensorflow,onnx}` | torch [BSD], candle [MIT/Apache-2.0], micrograd/nanoGPT [MIT], onnx [Apache-2.0] | permissive | needs notebook |
| C | C3 | NLP / embeddings / vector search (tokenization → ANN → vector DB) | — | `architecture/{sentence-transformers,faiss,chroma}` (missing: transformers, tokenizers) | tokenizers/tiktoken [Apache-2.0/MIT], sentence-transformers [Apache-2.0], faiss [MIT], chroma [Apache-2.0], qdrant [Apache-2.0] | permissive | needs notebook |
| D | D1 | Data & eval harness (metrics → regression gates → experiment logs) | ✎ `../learning-ai-tuning/notebooks/eval/001_eval_harness.py` | `architecture/{axolotl,accelerate,optimum}` (D2 systems this gates) | scikit-learn [BSD], stdlib json/sqlite3 [PSF]; next: datasets/evaluate [Apache-2.0], lm-eval-harness [MIT] | permissive | existing |

Notes:

- `✎` marks a curriculum living in a sibling `learning-*` repo (relative paths from
  this repo's root). `architecture/<project>/` paths are all **verified present** in
  the corpus; gaps are listed inline as `missing:` and imply
  `needs architecture link` for those specific packages.
- D/E/F build order (from the taxonomy artifact): D1 eval harness first
  ("you can't tune what you can't measure") → D2 fine-tuning → D3 alignment;
  E and F notebooks start here (`notebooks/ai_serving/`, `notebooks/enterprise/`)
  when their first topics arrive — the D1 gate is satisfied by
  `../learning-ai-tuning/`.

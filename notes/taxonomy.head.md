# Learning Taxonomy Index

The bridge between the two study corpora:

1. **Curriculum mode** — `learning-*` sibling repos with `notes/` progressions and
   marimo notebooks (PEP 723, `uv --sandbox`). This repo's rules: `AGENTS.md`.
2. **Architecture-study mode** — deep source reads under the work-notes corpus,
   referenced below as `architecture/<project>/` (146 project dirs at last count).

Each row indexes one taxonomy track. Notebooks for **any** domain are born in this
repo under `notebooks/<domain>/<library>/`; sibling `learning-<track>` repos are
optional — a track graduates only if it outgrows this repo (as `learning-ai-tuning`
did for the eval-harness track).

**Mastery ladder** (orthogonal to domains — the rung a row's current artifact teaches):

- **fundamentals** — build the concept from first principles, stdlib-first
- **self-sufficiency** — drive the real library competently
- **reproducible** — compose tools; interop, caching, tests as one system
- **production** — org-scale patterns: orchestration, messaging, load, governance

**License policy:** notebook PEP 723 dependencies must be permissive
(MIT/BSD/Apache-2.0/PSF/ISC). MPL-2.0 is dev/test-only and flagged `⚑`.
GPL/AGPL/SSPL/BUSL/RSAL targets are *study-only* — read in architecture mode,
never a dependency. License unclear → `study-only` until verified.

**Statuses:** `existing` · `seed` (entry-point notebook exists; depth pending) ·
`needs notebook` · `needs architecture link` · `needs license verification` ·
`study-only` · `deferred`

# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
#     "tokenizers",
# ]
# ///

"""tokenizers — BPE from scratch: the merge loop by hand, then the Rust library (C3, L1)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="tokenizers: BPE from scratch")


with app.setup:
    from itertools import pairwise

    import marimo as mo
    from tokenizers import Tokenizer, models, pre_tokenizers, trainers


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Byte-pair encoding, by hand

    Every LLM's vocabulary starts here: count adjacent symbol pairs, merge
    the most frequent, repeat. This notebook implements the merge loop in
    ~25 stdlib lines on the classic `low/lower/newest/widest` corpus, then
    trains HuggingFace `tokenizers` (the Rust library) on the same data and
    compares what each learned.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/huggingface/tokenizers>
    - In the source:
      `tokenizers/src/models/bpe/trainer.rs` is this notebook's loop, in Rust
      with word-level parallelism
    - The 1994/2016 lineage: Gage's compression BPE → Sennrich et al.'s
      subword NMT (whose worked example this corpus is)
    """)
    return


@app.function
def pair_counts(vocab: dict[tuple[str, ...], int]) -> dict[tuple[str, str], int]:
    """Count adjacent symbol pairs across the weighted word vocabulary."""
    counts: dict[tuple[str, str], int] = {}
    for symbols, freq in vocab.items():
        for left, right in pairwise(symbols):
            counts[(left, right)] = counts.get((left, right), 0) + freq
    return counts


@app.function
def merge_pair(
    vocab: dict[tuple[str, ...], int], pair: tuple[str, str]
) -> dict[tuple[str, ...], int]:
    """Rewrite every word, fusing occurrences of `pair` into one symbol."""
    merged: dict[tuple[str, ...], int] = {}
    for symbols, freq in vocab.items():
        out: list[str] = []
        i = 0
        while i < len(symbols):
            if i + 1 < len(symbols) and (symbols[i], symbols[i + 1]) == pair:
                out.append(symbols[i] + symbols[i + 1])
                i += 2
            else:
                out.append(symbols[i])
                i += 1
        merged[tuple(out)] = merged.get(tuple(out), 0) + freq
    return merged


@app.function
def bpe_train(words: dict[str, int], num_merges: int) -> list[tuple[str, str]]:
    """The whole algorithm: repeatedly merge the most frequent adjacent pair."""
    vocab: dict[tuple[str, ...], int] = {(*word, "</w>"): freq for word, freq in words.items()}
    merges: list[tuple[str, str]] = []
    for _ in range(num_merges):
        counts = pair_counts(vocab)
        if not counts:
            break
        # Highest count wins; ties go to the lexicographically smallest pair
        # (the corpus has a three-way tie at 9: e+s, s+t, t+</w>).
        best = min(counts, key=lambda p: (-counts[p], p))
        merges.append(best)
        vocab = merge_pair(vocab, best)
    return merges


@app.function
def corpus_words() -> dict[str, int]:
    """Sennrich et al.'s worked example: word -> frequency."""
    return {"low": 5, "lower": 2, "newest": 6, "widest": 3}


@app.cell
def _():
    n_merges = mo.ui.slider(1, 12, value=6, label="number of merges")
    n_merges
    return (n_merges,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The merge loop, step by step
    """)
    return


@app.cell
def _(n_merges):
    merges = bpe_train(corpus_words(), n_merges.value)
    mo.vstack(
        [
            mo.md(
                "**The learned merges, in order** — `('e','s')` wins first"
                " because *newest* + *widest* contribute 9 occurrences of"
                " `e s`:"
            ),
            mo.ui.table(
                [
                    {"step": i + 1, "merge": f"{left} + {right}", "new symbol": left + right}
                    for i, (left, right) in enumerate(merges)
                ]
            ),
        ],
        gap=0.5,
    )
    return (merges,)


@app.cell
def _(merges):
    _vocab: dict[tuple[str, ...], int] = {
        (*word, "</w>"): freq for word, freq in corpus_words().items()
    }
    for _pair in merges:
        _vocab = merge_pair(_vocab, _pair)
    mo.vstack(
        [
            mo.md("**Words as the merge loop now sees them** — subwords emerge:"),
            mo.ui.table(
                [
                    {
                        "word": "".join(s.replace("</w>", "") for s in symbols),
                        "segmentation": " · ".join(symbols),
                        "freq": freq,
                    }
                    for symbols, freq in _vocab.items()
                ]
            ),
        ],
        gap=0.5,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## The Rust library on the same corpus

    `tokenizers` trains in-memory from an iterator — no files, no network.
    Same algorithm (plus an alphabet pass and parallel counting), so the
    early merges should look familiar.
    """)
    return


@app.cell
def _(n_merges):
    hf = Tokenizer(models.BPE())
    hf.pre_tokenizer = pre_tokenizers.Whitespace()
    _lines = [" ".join([w] * f) for w, f in corpus_words().items()]
    _alphabet_size = len({ch for w in corpus_words() for ch in w})
    hf.train_from_iterator(
        _lines,
        trainers.BpeTrainer(
            vocab_size=_alphabet_size + n_merges.value,
            show_progress=False,
        ),
    )
    _encoded = hf.encode("lowest").tokens
    mo.vstack(
        [
            mo.md(
                f"Library vocab size **{hf.get_vocab_size()}** (alphabet"
                f" {_alphabet_size} + {n_merges.value} merges) ·"
                f" `encode('lowest')` → `{_encoded}` — *lowest* never appeared"
                " in the corpus, yet its pieces did. That generalization is"
                " the entire point of subword tokenization."
            ),
        ]
    )
    return (hf,)


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Scratch vs library — what differs": mo.md(
                """
    - the library tracks an explicit **alphabet** stage (every character
      is a token before any merge)
    - word-end is modeled by the pre-tokenizer's offsets, not a literal
      `</w>` symbol
    - counting is parallel (Rust + rayon) — same argmax, different speed
    """
            ),
            "TODO(you): break the tie-break": mo.md(
                """
    At merge step where two pairs tie, our scratch loop breaks ties
    lexicographically; the library has its own order. Construct a corpus
    where the two diverge by step 3, and explain which choice produces
    the shorter encoding of a held-out word.
    """
            ),
        }
    )
    return


@app.cell
def test_bpe(hf):
    # The textbook first merge: 'e'+'s' from newest(6) + widest(3) = 9 pairs.
    _merges = bpe_train(corpus_words(), 4)
    assert _merges[0] == ("e", "s"), _merges
    assert _merges[1] == ("es", "t"), _merges
    # The library generalizes to an unseen word using learned subwords.
    _tokens = hf.encode("lowest").tokens
    assert "".join(_tokens) == "lowest"
    assert 1 < len(_tokens) <= 4, _tokens
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - C3 · L2: `ml/faiss/001_ann_vector_search.py` — once text is tokens and
      tokens become vectors, retrieval needs an index
    - The run-store series in `../learning-ai-tuning` searches *metadata*;
      this rung is about searching *meaning*
    """)
    return


if __name__ == "__main__":
    app.run()

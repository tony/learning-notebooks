# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""torch — autograd (md-first seed): the walkthrough to run locally with torch installed."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="torch: autograd (seed)")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # torch: autograd — md-first seed

    Seed notebook (taxonomy C2). **torch is deliberately NOT a dependency
    here**: its wheels are too heavy for the CI smoke-run, so this seed carries
    the walkthrough as annotated code to run locally. To promote it to a live
    notebook:

    ```bash
    uv add --script notebooks/ml/torch/001_autograd.py torch
    uv run marimo edit --sandbox notebooks/ml/torch/001_autograd.py
    ```

    …then move the fenced code into real cells and **keep it off the CI
    smoke list** (AGENTS.md "CI-safety").
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/pytorch/pytorch>
    - In the source: start at
      `torch/autograd/` and `torch/csrc/autograd/` (the tape).
    - Architecture corpus: the `pytorch` study (117 files); `candle` (94) shows
      the same machinery in Rust.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## The walkthrough (run locally)

    Autograd is a tape: every op on a `requires_grad` tensor records a node;
    `backward()` replays the tape in reverse, accumulating into `.grad`.

    ```python
    import torch

    # 1. Leaves: tensors that want gradients
    w = torch.tensor([1.5, -2.0], requires_grad=True)
    x = torch.tensor([3.0, 4.0])

    # 2. Forward pass builds the graph as a side effect
    loss = ((w * x).sum() - 1.0) ** 2
    loss.grad_fn          # <PowBackward0> — the tape's last node

    # 3. Reverse pass: d(loss)/d(w) lands in w.grad
    loss.backward()
    w.grad                # tensor([-33., -44.])  == 2*(w·x - 1) * x

    # 4. Gradients ACCUMULATE — zero them between steps
    w.grad.zero_()

    # 5. Opt out for inference
    with torch.no_grad():
        prediction = (w * x).sum()
    ```

    Things to verify while running it: `loss.grad_fn.next_functions` walks the
    tape; `x.grad` is `None` (not a leaf that requires grad); re-calling
    `backward()` without `retain_graph=True` raises — the tape is freed.
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


if __name__ == "__main__":
    app.run()

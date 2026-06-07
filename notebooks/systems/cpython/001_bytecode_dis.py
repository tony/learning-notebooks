# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""cpython — bytecode & dis: what your functions compile to (A1, L1 fundamentals)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="cpython: bytecode & dis")


with app.setup:
    import dis

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # What Python compiles to: bytecode, by `dis`

    Every `def` compiles to a **code object** executed by a **stack machine**
    (the eval loop in `Python/ceval.c`). The stdlib `dis` module is the
    window: this notebook reads real disassembly, inspects code objects, and
    traces one expression through the stack — L1 fundamentals for everything
    in domain A.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/python/cpython>
    - Local clone (relative): `../../c/cpython` — `Python/ceval.c` (the
      switch at the heart of the interpreter), `Python/compile.c`
      (AST → bytecode), `Include/opcode_ids.h`
    - Architecture corpus: the `cpython` study (103 files) maps the runtime.
    - Taxonomy row: A1 in `notes/taxonomy.md`.
    """)
    return


@app.function
def weighted_sum(a: float, b: float, c: float) -> float:
    """The traced example: one multiply, one add."""
    return a + b * c


@app.function
def squares_loop(n: int) -> list[int]:
    """Accumulator loop — compare its bytecode with the comprehension."""
    out: list[int] = []
    for i in range(n):
        out.append(i * i)  # noqa: PERF401 — the loop IS the specimen under the microscope
    return out


@app.function
def squares_comprehension(n: int) -> list[int]:
    """Same result, comprehension form — fewer, more specialized instructions."""
    return [i * i for i in range(n)]


@app.cell
def _():
    picker = mo.ui.dropdown(
        ["weighted_sum", "squares_loop", "squares_comprehension"],
        value="weighted_sum",
        label="disassemble",
    )
    picker
    return (picker,)


@app.cell
def _(picker):
    _fns = {
        "weighted_sum": weighted_sum,
        "squares_loop": squares_loop,
        "squares_comprehension": squares_comprehension,
    }
    mo.plain_text(dis.Bytecode(_fns[picker.value]).dis())
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Tracing `a + b * c` through the stack

    The compiler already encoded precedence — there is no operator table at
    runtime, just push/pop order:

    | step | instruction | stack after |
    |---|---|---|
    | 1 | `LOAD_FAST a` | `a` |
    | 2 | `LOAD_FAST b` | `a, b` |
    | 3 | `LOAD_FAST c` | `a, b, c` |
    | 4 | `BINARY_OP *` | `a, (b*c)` |
    | 5 | `BINARY_OP +` | `(a + b*c)` |
    | 6 | `RETURN_VALUE` | — |

    (On 3.14 you'll see `LOAD_FAST_BORROW` — same load, but borrowing the
    reference instead of incref'ing it: the interpreter evolves under your
    feet, which is rather the point of disassembling it.)
    """)
    return


@app.cell
def _():
    _code = weighted_sum.__code__
    mo.vstack(
        [
            mo.md(
                "**The code object** is the compilation artifact — constants,"
                " names, and layout the eval loop consumes:"
            ),
            mo.tree(
                {
                    "co_name": _code.co_name,
                    "co_varnames": _code.co_varnames,
                    "co_consts": _code.co_consts,
                    "co_argcount": _code.co_argcount,
                    "co_stacksize": _code.co_stacksize,
                }
            ),
        ],
        gap=0.5,
    )
    return


@app.cell
def _():
    _loop_n = len(list(dis.get_instructions(squares_loop)))
    _comp_n = len(list(dis.get_instructions(squares_comprehension)))
    mo.hstack(
        [
            mo.stat(value=_loop_n, label="loop instructions", bordered=True),
            mo.stat(value=_comp_n, label="comprehension instructions", bordered=True),
            mo.stat(
                value=f"{_comp_n - _loop_n:+d}",
                label="delta",
                caption="static size ≠ runtime cost",
                bordered=True,
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "What to notice in the loop vs the comprehension": mo.md(
                """
    Counterintuitively, the comprehension can have **more** static
    instructions (its 3.12+ inlining adds setup/teardown) — but look at
    the **hot path**: the loop executes `append` as an attribute load
    plus a full `CALL` *every iteration*, while the comprehension's body
    is a single specialized `LIST_APPEND` opcode. Static instruction
    count is not runtime cost; what repeats is what matters.
    """
            ),
            "TODO(you): one surprising opcode": mo.md(
                """
    Disassemble a stdlib function you use daily (`dis.dis(json.dumps)`)
    and find one opcode you can't explain. Chase it through
    `../../c/cpython/Python/ceval.c` — the handler is a `TARGET(...)`
    block. Write down what it does.
    """
            ),
        }
    )
    return


@app.cell
def test_bytecode_shapes():
    _names = {ins.opname for ins in dis.get_instructions(weighted_sum)}
    # 3.13: LOAD_FAST / LOAD_FAST_LOAD_FAST; 3.14: LOAD_FAST_BORROW variants.
    assert any(name.startswith("LOAD_FAST") for name in _names), _names
    assert any(ins.opname.startswith("BINARY_OP") for ins in dis.get_instructions(weighted_sum))
    assert weighted_sum.__code__.co_varnames == ("a", "b", "c")
    # Hot paths differ by construction: the loop CALLs append every
    # iteration; the comprehension uses the specialized LIST_APPEND opcode.
    _loop_ops = {ins.opname for ins in dis.get_instructions(squares_loop)}
    _comp_ops = {ins.opname for ins in dis.get_instructions(squares_comprehension)}
    assert any(op.startswith("CALL") for op in _loop_ops), _loop_ops
    assert "LIST_APPEND" in _comp_ops, _comp_ops
    assert "LIST_APPEND" not in _loop_ops
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - A1 deeper: GC and refcounting (`../../c/cpython/Python/gc.c`), then the
      specializing adaptive interpreter (PEP 659)
    - Sibling rungs: `notes/taxonomy.md` — this was L1; the A-domain L2 seeds
      (anyio, sortedcontainers, rich) drive real libraries
    """)
    return


if __name__ == "__main__":
    app.run()

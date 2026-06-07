# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""presidio — PII governance from scratch: detect, redact, audit (F4, L4)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="enterprise: PII governance")


with app.setup:
    import hashlib
    import re

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Governance in three verbs: detect, redact, audit

    Before any text leaves a system — logs, LLM prompts, analytics exports —
    something must answer *does this contain PII?* This notebook builds the
    minimal honest version: regex detectors plus a **Luhn check** (pattern
    alone over-fires on card numbers; the checksum is the difference between
    a finding and noise), redaction that preserves structure, and a
    salted-hash **audit trail** that can prove *what* was redacted without
    storing it.

    Meta-note: this repo already practices F4 — the `git grep '/home/'`
    quality gate is a PII detector wired into CI.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/microsoft/presidio>
    - Local clone (relative): `../presidio` — `presidio-analyzer/` (recognizer
      registry: the productionized version of this notebook's detector list)
    - Architecture corpus: the `presidio` study; `opensearch` covers the
      audit-log side at scale.
    - Taxonomy row: F4 · mastery L4 in `notes/taxonomy.md`.
    """)
    return


@app.function
def luhn_ok(digits: str) -> bool:
    """The card-number checksum: doubles every second digit from the right."""
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


@app.function
def scan_pii(text: str) -> list[dict]:
    """Find emails, phone numbers, and Luhn-valid card numbers with spans."""
    findings: list[dict] = []
    patterns = {
        "email": r"[\w.+-]+@[\w-]+\.[\w.]+",
        "phone": r"\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}",
        "card": r"(?:\d[ -]?){13,19}",
    }
    for kind, pattern in patterns.items():
        for match in re.finditer(pattern, text):
            value = match.group()
            if kind == "card":
                digits = re.sub(r"\D", "", value)
                if not (13 <= len(digits) <= 19 and luhn_ok(digits)):
                    continue  # the checksum separates findings from noise
            findings.append(
                {"kind": kind, "value": value.strip(), "start": match.start(), "end": match.end()}
            )
    return findings


@app.function
def redact(text: str, findings: list[dict]) -> str:
    """Replace each finding with a typed placeholder, right-to-left to keep spans valid."""
    out = text
    for f in sorted(findings, key=lambda f: -f["start"]):
        out = out[: f["start"]] + f"<{f['kind'].upper()}>" + out[f["end"] :]
    return out


@app.function
def audit_records(findings: list[dict], salt: str = "rotate-me-per-deployment") -> list[dict]:
    """Salted hashes prove WHAT was redacted without storing the value itself."""
    return [
        {
            "kind": f["kind"],
            "digest": hashlib.sha256((salt + f["value"]).encode()).hexdigest()[:16],
            "span": f"{f['start']}-{f['end']}",
        }
        for f in findings
    ]


@app.function
def sample_log() -> str:
    """Synthetic support-ticket text with planted (fake) PII."""
    return (
        "Customer ada.lovelace@example.com called from (555) 867-5309 about a "
        "failed charge on card 4539 1488 0343 6467. Order #88-1042 shipped. "
        "Unrelated number sequence 1234 5678 9012 3456 should NOT match (bad "
        "checksum), and support@example.com followed up."
    )


@app.cell
def _():
    doc = mo.ui.text_area(value=sample_log(), label="text to scan", rows=5, full_width=True)
    doc
    return (doc,)


@app.cell
def _(doc):
    found = scan_pii(doc.value)
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.stat(value=len(found), label="findings", bordered=True),
                    mo.stat(
                        value=len({f["kind"] for f in found}), label="PII types", bordered=True
                    ),
                    mo.stat(
                        value="Luhn",
                        label="card validator",
                        caption="pattern + checksum, not pattern alone",
                        bordered=True,
                    ),
                ],
                gap=1,
            ),
            mo.ui.table([{k: f[k] for k in ("kind", "value", "start", "end")} for f in found])
            if found
            else mo.callout("No PII found.", kind="success"),
        ],
        gap=0.5,
    )
    return (found,)


@app.cell
def _(doc, found):
    mo.vstack(
        [
            mo.md("**Redacted** (structure preserved — downstream parsers keep working):"),
            mo.plain_text(redact(doc.value, found)),
            mo.md("**Audit trail** (salted digests — provable, not recoverable):"),
            mo.ui.table(audit_records(found)),
        ],
        gap=0.5,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Why the bad-checksum decoy matters": mo.md(
                """
    `1234 5678 9012 3456` looks exactly like a card to a regex. Luhn
    rejects it — precision is the hard half of detection. Presidio's
    recognizers each carry this shape: pattern + validator + confidence
    score, registered per entity type.
    """
            ),
            "Promotion path (off-CI)": mo.md(
                """
    `uv add --script <this file> presidio-analyzer` brings NER-backed
    recognition (names, locations) — but it downloads a spaCy model, so
    per AGENTS.md CI-safety it never joins the smoke list. The detector
    *interface* you'd plug into is the one above.
    """
            ),
            "TODO(you): the gate": mo.md(
                """
    Write the CI version: a script that scans `notebooks/**/*.py` md
    strings with `scan_pii` and fails on findings — then decide: should
    the planted fakes in THIS notebook trip it? Design the allowlist
    (this repo's `/home/` gate solves the same problem with scoping).
    """
            ),
        }
    )
    return


@app.cell
def test_governance():
    _findings = scan_pii(sample_log())
    _kinds = sorted(f["kind"] for f in _findings)
    # Both emails, the phone, and exactly ONE card (the Luhn-valid one).
    assert _kinds == ["card", "email", "email", "phone"], _kinds
    assert luhn_ok("4539148803436467") and not luhn_ok("1234567890123456")
    # Redaction removes every raw value.
    _clean = redact(sample_log(), _findings)
    assert all(f["value"] not in _clean for f in _findings)
    assert "<CARD>" in _clean and "<EMAIL>" in _clean and "<PHONE>" in _clean
    # Audit digests are stable, salted, and value-free.
    _audit = audit_records(_findings)
    assert len(_audit) == len(_findings)
    assert all(f["value"] not in str(_audit) for f in _findings)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - The full taxonomy now has a seed in every domain — see
      `notes/taxonomy.md` for the ladder view and `notes/study_plan.md`
      for what each rung grows into next
    - F4 backlog: presidio with NER, lineage, and the audit log living in
      something like `../learning-ai-tuning`'s run store
    """)
    return


if __name__ == "__main__":
    app.run()

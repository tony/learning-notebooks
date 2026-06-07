# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo",
# ]
# ///

"""kafka — event patterns without the broker: outbox, at-least-once, idempotent consumers (F1, L4)."""

import marimo

__generated_with = "0.23.8"
app = marimo.App(width="medium", app_title="enterprise: event patterns")


with app.setup:
    import json
    import sqlite3

    import marimo as mo


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    # Event-driven patterns, brokerless

    The hard parts of Kafka aren't Kafka — they're the **delivery contracts**.
    This notebook builds the three load-bearing patterns on stdlib sqlite:

    1. **Transactional outbox** — the business write and its event commit
       *atomically*, so no event is ever lost or phantom
    2. **At-least-once delivery** — the relay retries, so duplicates are a
       *feature* of the contract, not a bug
    3. **Idempotent consumer** — dedup by event id makes duplicates harmless

    Map them onto a real broker afterward and Kafka reads like an
    implementation detail.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Source reading

    - Upstream: <https://github.com/apache/kafka>
    - Local clone (relative): `../../java/kafka` — `core/src/main/scala/kafka/log/`
      (the commit log these patterns assume)
    - Architecture corpus: the `kafka` study (185 files) and `pulsar` (the
      same contracts, different log).
    - Taxonomy row: F1 · mastery L4 in `notes/taxonomy.md`.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.mermaid(
        """
    graph LR
        APP[order write] -->|same txn| ORD[(orders)]
        APP -->|same txn| OUT[(outbox)]
        OUT -->|relay, retried| TOPIC[(topic log)]
        TOPIC --> CONS[consumer]
        CONS -->|dedup on event_id| EFF[(side effects)]
    """
    )
    return


@app.function
def place_order(db: "sqlite3.Connection", order_id: int, sku: str, qty: int) -> None:
    """The outbox pattern: business row + event row in ONE transaction."""
    with db:  # one atomic transaction — both rows or neither
        db.execute("INSERT INTO orders VALUES (?, ?, ?)", (order_id, sku, qty))
        db.execute(
            "INSERT INTO outbox (event_id, payload) VALUES (?, ?)",
            (f"order-{order_id}", json.dumps({"order_id": order_id, "sku": sku, "qty": qty})),
        )


@app.function
def relay_outbox(db: "sqlite3.Connection") -> int:
    """Publish outbox rows to the topic. At-least-once: running it twice re-publishes
    anything not yet marked, and a crash between publish and mark does the same.
    """
    rows = db.execute("SELECT event_id, payload FROM outbox WHERE published = 0").fetchall()
    for event_id, payload in rows:
        db.execute("INSERT INTO topic (event_id, payload) VALUES (?, ?)", (event_id, payload))
        # A real relay can die RIGHT HERE — after publish, before the mark.
    db.execute("UPDATE outbox SET published = 1 WHERE published = 0")
    db.commit()
    return len(rows)


@app.function
def consume_topic(db: "sqlite3.Connection") -> dict[str, int]:
    """Idempotent consumer: process each event_id exactly once, however often delivered."""
    processed = skipped = 0
    for event_id, payload in db.execute("SELECT event_id, payload FROM topic ORDER BY rowid"):
        already = db.execute("SELECT 1 FROM processed WHERE event_id = ?", (event_id,)).fetchone()
        if already:
            skipped += 1
            continue
        record = json.loads(payload)
        with db:
            db.execute(
                "INSERT INTO shipments (order_id, qty) VALUES (?, ?)",
                (record["order_id"], record["qty"]),
            )
            db.execute("INSERT INTO processed (event_id) VALUES (?)", (event_id,))
        processed += 1
    return {"processed": processed, "skipped": skipped}


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Five orders, one crashed relay
    """)
    return


@app.cell
def _():
    bus = sqlite3.connect(":memory:")
    bus.executescript(
        """
        CREATE TABLE orders    (order_id INTEGER PRIMARY KEY, sku TEXT, qty INTEGER);
        CREATE TABLE outbox    (event_id TEXT PRIMARY KEY, payload TEXT, published INTEGER DEFAULT 0);
        CREATE TABLE topic     (seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT, payload TEXT);
        CREATE TABLE processed (event_id TEXT PRIMARY KEY);
        CREATE TABLE shipments (order_id INTEGER, qty INTEGER);
        """
    )
    for _i, (_sku, _qty) in enumerate(
        [("widget", 3), ("gizmo", 1), ("widget", 7), ("doodad", 2), ("gizmo", 5)], start=1
    ):
        place_order(bus, _i, _sku, _qty)

    # The retry that at-least-once promises: simulate a crashed relay by
    # publishing once WITHOUT marking, then running the proper relay.
    for _eid, _payload in bus.execute("SELECT event_id, payload FROM outbox WHERE published = 0"):
        bus.execute("INSERT INTO topic (event_id, payload) VALUES (?, ?)", (_eid, _payload))
    relay_outbox(bus)  # re-publishes everything: duplicates now exist

    stats = consume_topic(bus)
    return bus, stats


@app.cell
def _(bus, stats):
    _orders = bus.execute("SELECT count(*) FROM orders").fetchone()[0]
    _topic = bus.execute("SELECT count(*) FROM topic").fetchone()[0]
    _ship = bus.execute("SELECT count(*) FROM shipments").fetchone()[0]
    mo.hstack(
        [
            mo.stat(value=_orders, label="orders written", bordered=True),
            mo.stat(
                value=_topic,
                label="topic deliveries",
                caption="duplicates by design (crashed relay)",
                bordered=True,
            ),
            mo.stat(
                value=_ship,
                label="shipments created",
                caption=f"{stats['skipped']} duplicates skipped",
                bordered=True,
            ),
        ],
        gap=1,
    )
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Exactly-once effects

    Ten deliveries, five shipments — **exactly-once *effect* on top of
    at-least-once *delivery***. That sentence is most of event-driven
    architecture; everything else is throughput.
    """)
    return


@app.cell(hide_code=True)
def _():
    mo.accordion(
        {
            "Mapping to the real thing": mo.md(
                """
    | here (sqlite) | Kafka |
    |---|---|
    | `topic` table, `seq` rowid | partition + offset |
    | `relay_outbox` | Kafka Connect / Debezium outbox relay |
    | `processed` table | consumer-side dedup store (or idempotent producer ids) |
    | `with db:` transaction | the producer transaction API |
    | re-running the relay | retries after a missed ack |
    """
            ),
            "TODO(you): consumer groups": mo.md(
                """
    Split `consume_topic` into two consumers that each claim a subset of
    `event_id`s (hash mod 2 — that's partitioning). What new failure mode
    appears if both might process the *same* id, and which table prevents
    it?
    """
            ),
        }
    )
    return


@app.cell
def test_delivery_contracts(bus, stats):
    _orders = bus.execute("SELECT count(*) FROM orders").fetchone()[0]
    _topic = bus.execute("SELECT count(*) FROM topic").fetchone()[0]
    _ship = bus.execute("SELECT count(*) FROM shipments").fetchone()[0]
    # Duplicates really happened (at-least-once), and effects stayed exact.
    assert _topic == 2 * _orders, (_topic, _orders)
    assert _ship == _orders
    assert stats == {"processed": _orders, "skipped": _orders}
    # Replaying the whole topic again changes nothing — idempotent.
    _again = consume_topic(bus)
    assert _again["processed"] == 0
    assert bus.execute("SELECT count(*) FROM shipments").fetchone()[0] == _orders
    return


@app.cell(hide_code=True)
def _():
    mo.md(r"""
    ## Where this goes next

    - F2: who *runs* the relay on a schedule —
      `enterprise/airflow/001_dag_from_scratch.py`
    - The same outbox table pattern appears in `../learning-ai-tuning`'s run
      store: one storage idea, two domains
    """)
    return


if __name__ == "__main__":
    app.run()

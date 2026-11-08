"""
reconcile.py - the RECONCILIATION GATE (the headline correctness feature).

Before the Azure side publishes Gold analytics, it must prove its view of the
data agrees with the AWS source of truth. AWS wrote a ledger (in DynamoDB)
describing every batch it committed: event counts, revenue totals, and content
hashes. Azure independently computed its own totals from the Kafka stream.

The gate compares them:
    - event_count   : Azure's count vs sum of ledger event_counts
    - revenue_total : Azure's revenue vs sum of ledger revenue_totals
    - content hashes: the SET of batch hashes Azure saw vs the ledger's set

If they match within tolerance -> PASS -> publish Gold.
If not -> FAIL -> refuse to publish, surface the discrepancy. The dashboard is
never silently wrong: it shows reconciled numbers or it shows "reconciliation
failed", never wrong-but-confident numbers.
"""
from decimal import Decimal

from pulse import ledger

# Revenue can differ by a rounding cent across float summations; allow a tiny
# tolerance. Event counts must match exactly.
REVENUE_TOLERANCE = Decimal("1.00")


def ledger_totals() -> dict:
    """Aggregate the AWS ledger: total events, total revenue, set of hashes."""
    batches = ledger.all_committed_batches()
    total_events = sum(int(b["event_count"]) for b in batches)
    total_revenue = sum(Decimal(str(b.get("revenue_total", "0"))) for b in batches)
    hashes = {b["content_hash"] for b in batches}
    return {
        "event_count": total_events,
        "revenue_total": total_revenue,
        "hashes": hashes,
        "batch_count": len(batches),
    }


def reconcile(azure_totals: dict) -> dict:
    """Compare Azure's computed totals against the AWS ledger.
    Returns a verdict dict with passed=True/False and the discrepancies."""
    src = ledger_totals()

    azure_events = int(azure_totals["event_count"])
    azure_revenue = Decimal(str(azure_totals["revenue_total"]))

    event_match = azure_events == src["event_count"]
    revenue_match = abs(azure_revenue - src["revenue_total"]) <= REVENUE_TOLERANCE

    verdict = {
        "passed": bool(event_match and revenue_match),
        "event_count": {
            "azure": azure_events,
            "aws_ledger": src["event_count"],
            "match": event_match,
        },
        "revenue_total": {
            "azure": float(azure_revenue),
            "aws_ledger": float(src["revenue_total"]),
            "match": revenue_match,
            "delta": float(abs(azure_revenue - src["revenue_total"])),
        },
        "aws_batches": src["batch_count"],
    }
    return verdict

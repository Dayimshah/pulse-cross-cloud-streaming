"""
stats.py - quick ledger summary. Sums event_count and revenue across all
committed batches so we know exactly how much real data is in the lake.
Run:  python -m pulse.stats
"""
from decimal import Decimal

from pulse import ledger


def run():
    batches = ledger.all_committed_batches()
    total_events = sum(int(b["event_count"]) for b in batches)
    total_revenue = sum(Decimal(str(b.get("revenue_total", "0"))) for b in batches)
    partitions = {}
    for b in batches:
        p = int(b["partition"])
        partitions.setdefault(p, {"batches": 0, "events": 0})
        partitions[p]["batches"] += 1
        partitions[p]["events"] += int(b["event_count"])

    print(f"Committed batches : {len(batches)}")
    print(f"Total events      : {total_events}")
    print(f"Total revenue      : ${total_revenue}")
    for p in sorted(partitions):
        s = partitions[p]
        print(f"  partition {p}: {s['batches']} batches, {s['events']} events")


if __name__ == "__main__":
    run()

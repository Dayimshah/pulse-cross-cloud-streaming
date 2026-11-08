"""
Exactly-once MECHANICS. These test the pure functions in ledger.py that make
the exactly-once + reconciliation guarantees possible - no AWS calls needed.
"""
import random

from pulse import ledger


def test_batch_id_is_deterministic():
    """Same partition + offset range -> same id. This is what makes a replay
    produce the SAME ledger key, so re-processing is detected and skipped."""
    a = ledger.batch_id(1, 0, 99)
    b = ledger.batch_id(1, 0, 99)
    assert a == b == "1-0-99"


def test_batch_id_differs_by_range():
    assert ledger.batch_id(1, 0, 99) != ledger.batch_id(1, 0, 100)
    assert ledger.batch_id(0, 0, 99) != ledger.batch_id(1, 0, 99)


def test_content_hash_is_order_independent(small_events):
    """THE KEY RECONCILIATION PROPERTY: AWS and Azure may read events in
    different orders, but must compute the SAME hash over the same SET."""
    shuffled = small_events[:]
    random.shuffle(shuffled)
    assert ledger.content_hash(small_events) == ledger.content_hash(shuffled)


def test_content_hash_changes_with_content(small_events):
    """Changing the event set must change the fingerprint (detects drift)."""
    modified = small_events[:-1]  # drop one event
    assert ledger.content_hash(small_events) != ledger.content_hash(modified)


def test_revenue_total_only_counts_purchases(small_events):
    manual = round(
        sum(e["amount"] for e in small_events if e["event_type"] == "purchase"), 2
    )
    assert ledger.revenue_total(small_events) == manual

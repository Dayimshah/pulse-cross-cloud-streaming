"""
The RECONCILIATION GATE. Proves the "never silently wrong" guarantee: when the
two clouds' totals agree the gate passes; when they disagree it BLOCKS.

We mock the AWS-ledger read (ledger_totals) so these run offline with no AWS
calls - the test is about the gate's decision logic, not DynamoDB.
"""
from decimal import Decimal

from pulse import reconcile


def _fake_ledger(monkeypatch, events, revenue, hashes=None):
    monkeypatch.setattr(reconcile, "ledger_totals", lambda: {
        "event_count": events,
        "revenue_total": Decimal(str(revenue)),
        "hashes": hashes or set(),
        "batch_count": 1,
    })


def test_gate_passes_when_totals_match(monkeypatch):
    _fake_ledger(monkeypatch, events=50100, revenue="837207.23")
    verdict = reconcile.reconcile({"event_count": 50100, "revenue_total": 837207.23})
    assert verdict["passed"] is True
    assert verdict["event_count"]["match"] is True
    assert verdict["revenue_total"]["match"] is True


def test_gate_blocks_on_event_count_mismatch(monkeypatch):
    """AWS saw 50100 events, Azure only 50000 -> data lost -> gate MUST block."""
    _fake_ledger(monkeypatch, events=50100, revenue="837207.23")
    verdict = reconcile.reconcile({"event_count": 50000, "revenue_total": 837207.23})
    assert verdict["passed"] is False
    assert verdict["event_count"]["match"] is False


def test_gate_blocks_on_revenue_mismatch(monkeypatch):
    """Revenue off by a lot -> gate blocks (dashboard would be wrong)."""
    _fake_ledger(monkeypatch, events=50100, revenue="837207.23")
    verdict = reconcile.reconcile({"event_count": 50100, "revenue_total": 800000.00})
    assert verdict["passed"] is False
    assert verdict["revenue_total"]["match"] is False


def test_gate_tolerates_rounding_cent(monkeypatch):
    """A sub-$1 rounding difference across float sums is allowed."""
    _fake_ledger(monkeypatch, events=100, revenue="1000.00")
    verdict = reconcile.reconcile({"event_count": 100, "revenue_total": 1000.49})
    assert verdict["passed"] is True  # within REVENUE_TOLERANCE


def test_gate_rejects_beyond_tolerance(monkeypatch):
    _fake_ledger(monkeypatch, events=100, revenue="1000.00")
    verdict = reconcile.reconcile({"event_count": 100, "revenue_total": 1002.00})
    assert verdict["passed"] is False

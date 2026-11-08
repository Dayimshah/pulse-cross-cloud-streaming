"""
The generator's PLANTED STRUCTURE. The analytics can only be trusted if the
synthetic data has the properties we claim - so we assert them at the source.
"""
from datetime import datetime, timedelta, timezone

from pulse.events import make_event

REQUIRED = {"event_id", "event_type", "user_id", "product_id",
            "category", "amount", "currency", "timestamp", "country"}


def test_every_event_has_required_fields():
    for _ in range(500):
        e = make_event(days_back=7)
        assert REQUIRED.issubset(e.keys())


def test_only_purchases_have_amount():
    for _ in range(1000):
        e = make_event(days_back=7)
        if e["event_type"] == "purchase":
            assert e["amount"] > 0
        else:
            assert e["amount"] == 0.0


def test_event_ids_are_unique():
    ids = {make_event()["event_id"] for _ in range(2000)}
    assert len(ids) == 2000  # uuid4 collisions are effectively impossible


def test_timestamps_fall_within_window():
    """days_back=30 must produce timestamps within the last ~31 days."""
    now = datetime.now(timezone.utc)
    earliest = now - timedelta(days=31)
    for _ in range(500):
        e = make_event(days_back=30)
        ts = datetime.fromisoformat(e["timestamp"])
        assert earliest <= ts <= now + timedelta(minutes=1)


def test_live_mode_is_now():
    """days_back=0 (live mode) stamps events at ~now."""
    e = make_event(days_back=0)
    ts = datetime.fromisoformat(e["timestamp"])
    assert abs((datetime.now(timezone.utc) - ts).total_seconds()) < 5

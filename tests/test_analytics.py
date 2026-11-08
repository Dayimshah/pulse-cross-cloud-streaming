"""
Analytics INVARIANTS - properties that must hold for ANY random input, not
hardcoded numbers. If the data generator changes, these still protect the
analytics' correctness (the Prism philosophy carried into Pulse).
"""
from pulse import analytics


def test_funnel_only_shrinks(events):
    """A funnel can only get smaller: views >= carts >= purchases. Always."""
    f = analytics.conversion_funnel(events)
    assert f["views"] >= f["add_to_cart"] >= f["purchase"]


def test_conversion_rates_are_fractions(events):
    """Every rate is a probability in [0, 1]."""
    f = analytics.conversion_funnel(events)
    for key in ("view_to_cart_rate", "cart_to_purchase_rate", "overall_conversion"):
        assert 0.0 <= f[key] <= 1.0


def test_revenue_only_from_purchases(events):
    """Revenue must equal the sum of purchase amounts - views/carts add $0."""
    totals = analytics.control_totals(events)
    manual = round(sum(e["amount"] for e in events if e["event_type"] == "purchase"), 2)
    assert abs(totals["revenue_total"] - manual) < 0.01
    # non-purchase events must carry zero amount
    assert all(e["amount"] == 0.0 for e in events if e["event_type"] != "purchase")


def test_category_revenue_never_negative(events):
    cats = analytics.category_breakdown(events)
    assert all(c["revenue"] >= 0 for c in cats)
    assert all(c["events"] > 0 for c in cats)


def test_top_products_sorted_desc(events):
    """Top products must be ranked by revenue, descending."""
    prods = analytics.top_products(events)
    revs = [p["revenue"] for p in prods]
    assert revs == sorted(revs, reverse=True)


def test_retention_never_exceeds_100pct(events):
    """No cohort can retain more than 100% of itself; week_0 is always 100%."""
    cohorts = analytics.retention_cohorts(events)
    assert cohorts, "expected at least one cohort"
    for c in cohorts:
        assert c["retention"]["week_0"] == 1.0           # baseline is the full cohort
        assert all(0.0 <= v <= 1.0 for v in c["retention"].values())


def test_event_count_matches(events):
    totals = analytics.control_totals(events)
    assert totals["event_count"] == len(events)


def test_revenue_over_time_is_chronological(events):
    pts = analytics.revenue_over_time(events)
    days = [p["day"] for p in pts]
    assert days == sorted(days)
    assert all(p["revenue"] >= 0 for p in pts)

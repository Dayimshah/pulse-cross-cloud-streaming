"""
analytics.py - the Gold-layer computations (the "insights").

Pure functions: given a list of events, compute the metrics. Keeping them pure
(no I/O) means the test suite can assert INVARIANTS on them directly - e.g.
"funnel steps only shrink", "retention never exceeds 100%", "revenue only comes
from purchases" - which is the correctness philosophy carried into analytics.
"""
from collections import defaultdict
from datetime import datetime


def _parse_day(ts: str) -> str:
    """'2026-11-03T21:17:00+00:00' -> '2026-11-03' (the day bucket)."""
    return datetime.fromisoformat(ts).strftime("%Y-%m-%d")


def _parse_week(ts: str) -> str:
    """ISO year-week bucket, e.g. '2026-W44' - used for retention cohorts."""
    d = datetime.fromisoformat(ts)
    iso = d.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def revenue_over_time(events: list[dict]) -> list[dict]:
    """Daily revenue (purchases only) - shows the 30-day trend + seasonality."""
    by_day = defaultdict(float)
    for e in events:
        if e.get("event_type") == "purchase":
            by_day[_parse_day(e["timestamp"])] += e.get("amount", 0.0)
    return [{"day": d, "revenue": round(v, 2)} for d, v in sorted(by_day.items())]


def conversion_funnel(events: list[dict]) -> dict:
    """views -> add_to_cart -> purchase counts, plus conversion rates.
    INVARIANT: each step <= the step before it (a funnel only shrinks)."""
    counts = defaultdict(int)
    for e in events:
        counts[e.get("event_type")] += 1
    views = counts.get("view", 0)
    carts = counts.get("add_to_cart", 0)
    purchases = counts.get("purchase", 0)
    return {
        "views": views,
        "add_to_cart": carts,
        "purchase": purchases,
        "view_to_cart_rate": round(carts / views, 4) if views else 0.0,
        "cart_to_purchase_rate": round(purchases / carts, 4) if carts else 0.0,
        "overall_conversion": round(purchases / views, 4) if views else 0.0,
    }


def top_products(events: list[dict], limit: int = 10) -> list[dict]:
    """Top products by purchase revenue."""
    rev = defaultdict(float)
    qty = defaultdict(int)
    for e in events:
        if e.get("event_type") == "purchase":
            rev[e["product_id"]] += e.get("amount", 0.0)
            qty[e["product_id"]] += 1
    ranked = sorted(rev.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return [{"product_id": p, "revenue": round(r, 2), "units": qty[p]} for p, r in ranked]


def category_breakdown(events: list[dict]) -> list[dict]:
    """Revenue + event volume per category."""
    rev = defaultdict(float)
    vol = defaultdict(int)
    for e in events:
        vol[e["category"]] += 1
        if e.get("event_type") == "purchase":
            rev[e["category"]] += e.get("amount", 0.0)
    return [{"category": c, "revenue": round(rev[c], 2), "events": vol[c]}
            for c in sorted(vol, key=lambda c: rev[c], reverse=True)]


def retention_cohorts(events: list[dict]) -> list[dict]:
    """Weekly retention cohorts: group users by the week they FIRST appeared,
    then measure how many return in each subsequent week.
    INVARIANT: week-0 retention is 100%; no later week exceeds it."""
    # user -> set of weeks active
    user_weeks = defaultdict(set)
    for e in events:
        user_weeks[e["user_id"]].add(_parse_week(e["timestamp"]))

    # Determine each user's first (cohort) week.
    all_weeks = sorted({w for ws in user_weeks.values() for w in ws})
    week_index = {w: i for i, w in enumerate(all_weeks)}

    cohorts = defaultdict(lambda: defaultdict(set))  # cohort_week -> offset -> users
    for user, weeks in user_weeks.items():
        first = min(weeks, key=lambda w: week_index[w])
        base = week_index[first]
        for w in weeks:
            offset = week_index[w] - base
            cohorts[first][offset].add(user)

    result = []
    for cohort_week in sorted(cohorts, key=lambda w: week_index[w]):
        size = len(cohorts[cohort_week][0])
        if size == 0:
            continue
        offsets = {}
        for offset, users in sorted(cohorts[cohort_week].items()):
            offsets[f"week_{offset}"] = round(len(users) / size, 4)
        result.append({"cohort": cohort_week, "size": size, "retention": offsets})
    return result


def control_totals(events: list[dict]) -> dict:
    """The numbers the reconciliation gate checks against the AWS ledger."""
    total_revenue = round(
        sum(e.get("amount", 0.0) for e in events if e.get("event_type") == "purchase"), 2
    )
    return {"event_count": len(events), "revenue_total": total_revenue}


def compute_gold(events: list[dict]) -> dict:
    """The full Gold payload the dashboard reads from Cosmos."""
    return {
        "revenue_over_time": revenue_over_time(events),
        "funnel": conversion_funnel(events),
        "top_products": top_products(events),
        "categories": category_breakdown(events),
        "retention": retention_cohorts(events),
        "totals": control_totals(events),
    }

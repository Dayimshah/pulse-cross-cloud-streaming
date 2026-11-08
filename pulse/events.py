"""
events.py
Generates e-commerce transaction events (the data model from Step 2).

Two design goals that make the downstream analytics genuinely impressive:

1. PLANTED STRUCTURE the SQL/analytics layer can rediscover:
   - a realistic funnel (view > add_to_cart > purchase),
   - a stable, bounded user population so RETENTION / COHORT analysis has real
     repeat-visitor signal,
   - per-category price bands so revenue looks real.

2. REALISTIC TIME DISTRIBUTION across a 30-day history (not all "now"):
   - day-of-week seasonality (busier weekends),
   - hour-of-day seasonality (daytime/evening peaks),
   so windowed/trend analytics have many windows to plot and seasonality to show.

The 30-day span is deliberate: retention cohorts and week-over-week trends need
weeks of history, and those are the metrics that read best on a data resume.
"""
import random
import uuid
from datetime import datetime, timedelta, timezone

CATEGORIES = {
    "electronics": ["p_laptop", "p_phone", "p_headphones", "p_charger"],
    "apparel": ["p_tshirt", "p_jeans", "p_jacket", "p_socks"],
    "home": ["p_lamp", "p_mug", "p_cushion", "p_blanket"],
    "books": ["p_novel", "p_cookbook", "p_comic"],
}
COUNTRIES = ["IN", "US", "GB", "DE", "SG"]

PRICE_BANDS = {
    "electronics": (49.0, 999.0),
    "apparel": (9.0, 149.0),
    "home": (5.0, 89.0),
    "books": (4.0, 39.0),
}

EVENT_TYPE_WEIGHTS = [("view", 0.70), ("add_to_cart", 0.20), ("purchase", 0.10)]

# --- Seasonality weights -----------------------------------------------------
# Day of week (Mon=0 .. Sun=6): weekends busier.
DOW_WEIGHTS = [0.8, 0.85, 0.9, 1.0, 1.2, 1.6, 1.5]
# Hour of day (0..23): low overnight, peaks midday + evening.
HOUR_WEIGHTS = [
    0.2, 0.15, 0.1, 0.1, 0.15, 0.3, 0.5, 0.8, 1.0, 1.1, 1.2, 1.3,
    1.4, 1.3, 1.1, 1.0, 1.1, 1.3, 1.6, 1.7, 1.5, 1.1, 0.7, 0.4,
]

# Stable user population so the SAME users recur across days -> real retention.
_USER_POOL = [f"u_{i}" for i in range(1, 2001)]


def _weighted_choice(options_weights):
    r = random.random() * sum(w for _, w in options_weights)
    cumulative = 0.0
    for item, w in options_weights:
        cumulative += w
        if r <= cumulative:
            return item
    return options_weights[-1][0]


def _weighted_event_type() -> str:
    return _weighted_choice(EVENT_TYPE_WEIGHTS)


def _seasonal_timestamp(days_back: int) -> datetime:
    """Pick a timestamp within the last `days_back` days, weighted by
    day-of-week and hour-of-day seasonality so trends/peaks are visible."""
    now = datetime.now(timezone.utc)
    # Choose a day in the window, weighted by that day's DOW weight.
    day_options = []
    for d in range(days_back):
        day = now - timedelta(days=d)
        day_options.append((d, DOW_WEIGHTS[day.weekday()]))
    chosen_day = _weighted_choice([(d, w) for d, w in day_options])
    # Choose an hour weighted by hour-of-day seasonality.
    hour = int(_weighted_choice([(h, HOUR_WEIGHTS[h]) for h in range(24)]))
    base = now - timedelta(days=chosen_day)
    ts = base.replace(hour=hour, minute=random.randint(0, 59),
                      second=random.randint(0, 59), microsecond=0)
    # Guard: for "today" (chosen_day == 0) a random hour can land in the future
    # (e.g. hour 18 when it is currently 15:00). Never emit a future event -
    # future-dated data would corrupt today's analytics. Clamp to just before now.
    if ts > now:
        ts = now - timedelta(seconds=random.randint(1, 3600))
    return ts


def make_event(days_back: int = 0) -> dict:
    """Produce one transaction event matching the Step 2 schema.

    days_back = 0  -> timestamp is 'now' (live mode).
    days_back > 0  -> timestamp is spread across the last `days_back` days
                      with seasonality (backfill / historical mode).
    """
    category = random.choice(list(CATEGORIES.keys()))
    product_id = random.choice(CATEGORIES[category])
    event_type = _weighted_event_type()

    amount = 0.0
    if event_type == "purchase":
        low, high = PRICE_BANDS[category]
        amount = round(random.uniform(low, high), 2)

    if days_back > 0:
        ts = _seasonal_timestamp(days_back)
    else:
        ts = datetime.now(timezone.utc)

    return {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "user_id": random.choice(_USER_POOL),  # stable pool -> retention signal
        "product_id": product_id,
        "category": category,
        "amount": amount,
        "currency": "USD",
        "timestamp": ts.isoformat(),
        "country": random.choice(COUNTRIES),
    }

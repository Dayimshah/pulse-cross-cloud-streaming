"""
Shared test fixtures. A reusable synthetic event batch so every test runs
against realistic, randomized data - the point being that the INVARIANTS hold
no matter what random data is generated, not that specific numbers match.
"""
import random

import pytest

from pulse.events import make_event


@pytest.fixture
def events():
    """A fresh batch of 3,000 seasonal events spread over 14 days."""
    random.seed()  # genuinely random each run - invariants must survive any seed
    return [make_event(days_back=14) for _ in range(3000)]


@pytest.fixture
def small_events():
    """A tiny deterministic batch for hashing / id tests."""
    random.seed(42)
    return [make_event(days_back=7) for _ in range(50)]

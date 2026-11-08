"""
ledger.py
The transfer ledger - the brain of exactly-once + cross-cloud reconciliation.

Each processed micro-batch becomes ONE item in DynamoDB describing a contiguous
run of per-event offsets:

    batch_id      = "<partition>-<start_offset>-<end_offset>"   (deterministic PK)
    partition     = Kafka partition number
    start_offset  = first event's offset in the batch
    end_offset    = last event's offset in the batch   (inclusive)
    event_count   = number of events (end - start + 1)
    content_hash  = SHA-256 over the batch's event_ids -> fingerprint for reconciliation
    revenue_total = sum of purchase amounts (a control total both clouds must agree on)
    s3_key        = where the raw batch landed in Bronze
    status        = "committed"
    ts            = when it was written

Because batch_id is DETERMINISTIC (derived from partition + offset range), a
replay of the same events produces the SAME batch_id. That's what lets us detect
"already processed this run" and skip it -> idempotency.
"""
import hashlib
import json
import time

import boto3

from pulse import config

_dynamo = boto3.resource("dynamodb", region_name=config.AWS_REGION)
_table = _dynamo.Table(config.DYNAMODB_LEDGER_TABLE)


def batch_id(partition: int, start_offset: int, end_offset: int) -> str:
    """Deterministic primary key: same offset range -> same id -> safe replays."""
    return f"{partition}-{start_offset}-{end_offset}"


def content_hash(events: list[dict]) -> str:
    """SHA-256 fingerprint of the batch, built from sorted event_ids.
    Sorting makes it order-independent so AWS and Azure compute the SAME hash
    over the same set of events - the basis of the reconciliation gate."""
    ids = sorted(e["event_id"] for e in events)
    joined = "|".join(ids)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def revenue_total(events: list[dict]) -> float:
    """Control total: sum of purchase amounts. Both clouds must agree on this."""
    return round(sum(e.get("amount", 0.0) for e in events
                     if e.get("event_type") == "purchase"), 2)


def already_processed(bid: str) -> bool:
    """Idempotency check: have we already committed this exact batch?"""
    resp = _table.get_item(Key={"batch_id": bid})
    return "Item" in resp


def record_batch(partition: int, start_offset: int, end_offset: int,
                 events: list[dict], s3_key: str) -> dict:
    """Write the ledger entry for a successfully-stored batch.
    Called AFTER the raw events are durably in S3, BEFORE the Kafka offset
    is committed - the ordering that guarantees no loss and no duplicates."""
    bid = batch_id(partition, start_offset, end_offset)
    item = {
        "batch_id": bid,
        "partition": partition,
        "start_offset": start_offset,
        "end_offset": end_offset,
        "event_count": len(events),
        "content_hash": content_hash(events),
        # DynamoDB stores floats as Decimal; store revenue as a string to avoid
        # float/Decimal friction, parse back when reconciling.
        "revenue_total": str(revenue_total(events)),
        "s3_key": s3_key,
        "status": "committed",
        "ts": int(time.time()),
    }
    # Conditional put: only write if this batch_id doesn't already exist.
    # If two workers race on the same batch, exactly one wins - the other is a
    # no-op. Idempotency enforced at the database level, not just in code.
    try:
        _table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(batch_id)",
        )
    except _dynamo.meta.client.exceptions.ConditionalCheckFailedException:
        # Someone already wrote this exact batch - that's fine, it's idempotent.
        pass
    return item


def all_committed_batches() -> list[dict]:
    """Read every committed batch. Used by the Azure side to reconcile totals
    against what it independently computed."""
    items, resp = [], _table.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = _table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))
    return items

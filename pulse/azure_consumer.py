"""
azure_consumer.py - the ANALYTICS / SERVING side of the cross-cloud pipeline.

Key Kafka insight: this uses its OWN consumer group (pulse-azure-consumer),
separate from the AWS group. In Kafka, each consumer group gets the FULL stream
independently - so AWS and Azure both see all events, which is exactly what lets
us reconcile one cloud against the other.

Flow:
    1. read the full stream from Kafka (own group, from earliest)
    2. compute Silver (cleaned events) -> Blob
    3. compute Gold (funnel, revenue, cohorts, top products) -> Blob
    4. RECONCILE Azure's control totals against the AWS DynamoDB ledger
    5. gate: if reconciled -> publish Gold to Cosmos (dashboard reads it)
             if not       -> REFUSE to publish, write a failure marker

Run:  python -m pulse.azure_consumer
  IDLE_EXIT_SECONDS (default 10) -> drain the stream then compute + publish once.
"""
import io
import json
import os
from datetime import datetime, timezone

import pyarrow as pa
import pyarrow.parquet as pq
from azure.cosmos import CosmosClient, PartitionKey
from azure.storage.blob import BlobServiceClient
from confluent_kafka import Consumer

from pulse import analytics, config, reconcile

IDLE_EXIT_SECONDS = float(os.getenv("IDLE_EXIT_SECONDS", "10"))


def _build_consumer() -> Consumer:
    conf = config.kafka_common_config()
    conf.update({
        # Group id is overridable so we can recompute the whole stream on demand.
        # The analytics side recomputes Gold wholesale from the full history,
        # so reading from earliest each run is intentional, not stateful.
        "group.id": os.getenv("AZURE_GROUP_ID", "pulse-azure-consumer"),
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    return Consumer(conf)


def _drain_stream() -> list[dict]:
    """Read all currently-available events from Kafka into memory."""
    consumer = _build_consumer()
    consumer.subscribe([config.KAFKA_TOPIC])
    events, idle = [], 0.0
    print(f"Azure consumer draining '{config.KAFKA_TOPIC}'...", flush=True)
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                idle += 1.0
                if idle >= IDLE_EXIT_SECONDS:
                    break
                continue
            if msg.error():
                continue
            idle = 0.0
            events.append(json.loads(msg.value()))
            if len(events) % 10000 == 0:
                print(f"  read {len(events)} events...", flush=True)
    finally:
        consumer.close()
    print(f"  drained {len(events)} events.", flush=True)
    return events


def _blob_client() -> BlobServiceClient:
    conn = (f"DefaultEndpointsProtocol=https;AccountName={config.AZURE_STORAGE_ACCOUNT};"
            f"AccountKey={config.AZURE_STORAGE_KEY};EndpointSuffix=core.windows.net")
    return BlobServiceClient.from_connection_string(conn)


def _write_blob(container: str, name: str, payload: dict):
    bsc = _blob_client()
    blob = bsc.get_blob_client(container=container, blob=name)
    blob.upload_blob(json.dumps(payload, indent=2).encode("utf-8"), overwrite=True)


def _write_silver_parquet(container: str, name: str, events: list[dict]):
    """Silver layer as PARQUET: columnar + typed, the canonical medallion format
    for cleaned data. Written as a single Parquet file to Blob/ADLS Gen2.
    (Bronze stays raw JSON; Gold is served as JSON from Cosmos.)"""
    # Build a typed columnar table from the cleaned events.
    table = pa.Table.from_pylist([
        {
            "event_id": e["event_id"],
            "event_type": e["event_type"],
            "user_id": e["user_id"],
            "product_id": e["product_id"],
            "category": e["category"],
            "amount": float(e.get("amount", 0.0)),
            "currency": e.get("currency", "USD"),
            "timestamp": e["timestamp"],
            "country": e.get("country", ""),
        }
        for e in events
    ])
    buf = io.BytesIO()
    pq.write_table(table, buf, compression="snappy")
    buf.seek(0)
    bsc = _blob_client()
    blob = bsc.get_blob_client(container=container, blob=name)
    blob.upload_blob(buf.read(), overwrite=True)


def _publish_cosmos(gold: dict, verdict: dict):
    client = CosmosClient(config.COSMOS_ENDPOINT, credential=config.COSMOS_KEY)
    db = client.create_database_if_not_exists(config.COSMOS_DATABASE)
    container = db.create_container_if_not_exists(
        id=config.COSMOS_CONTAINER,
        partition_key=PartitionKey(path="/metric_type"),
    )
    published_at = datetime.now(timezone.utc).isoformat()
    # Each metric becomes one document the dashboard reads by metric_type.
    docs = {
        "revenue_over_time": gold["revenue_over_time"],
        "funnel": gold["funnel"],
        "top_products": gold["top_products"],
        "categories": gold["categories"],
        "retention": gold["retention"],
        "totals": gold["totals"],
        "reconciliation": verdict,
    }
    for metric_type, data in docs.items():
        container.upsert_item({
            "id": metric_type,
            "metric_type": metric_type,
            "data": data,
            "published_at": published_at,
        })


def run():
    events = _drain_stream()
    if not events:
        print("No events to process.")
        return

    # Silver: cleaned/validated events, written as Parquet (columnar + typed).
    silver = [e for e in events if e.get("event_id") and e.get("event_type")]
    _write_silver_parquet(
        "silver", f"silver-{datetime.now(timezone.utc):%Y%m%d%H%M%S}.parquet", silver)
    print(f"  Silver: {len(silver)} valid events written as Parquet.", flush=True)

    # Gold: the analytics.
    gold = analytics.compute_gold(silver)
    _write_blob("gold", "gold-latest.json", gold)
    print(f"  Gold computed. Totals: {gold['totals']}", flush=True)

    # THE GATE: reconcile Azure's totals against the AWS ledger.
    verdict = reconcile.reconcile(gold["totals"])
    print(f"  Reconciliation: {'PASS' if verdict['passed'] else 'FAIL'}", flush=True)
    print(f"    events  azure={verdict['event_count']['azure']} "
          f"aws={verdict['event_count']['aws_ledger']} "
          f"match={verdict['event_count']['match']}", flush=True)
    print(f"    revenue azure={verdict['revenue_total']['azure']} "
          f"aws={verdict['revenue_total']['aws_ledger']} "
          f"match={verdict['revenue_total']['match']}", flush=True)

    if verdict["passed"]:
        _publish_cosmos(gold, verdict)
        print("  GATE PASSED -> Gold published to Cosmos. Dashboard is live.", flush=True)
    else:
        _write_blob("gold", "RECONCILIATION_FAILED.json", verdict)
        print("  GATE FAILED -> refused to publish. Discrepancy recorded.", flush=True)


if __name__ == "__main__":
    run()

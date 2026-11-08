"""
aws_consumer.py  -  the SOURCE side of the cross-cloud pipeline.

A CONTINUOUS streaming consumer. It stays attached to the live Kafka stream
24/7 and never does "batch processing" in the ETL sense. The only batching is a
short micro-batch of the WRITES, to avoid the S3 small-files problem (same
pattern Spark Structured Streaming and the Kafka Connect S3 sink use).

THE EXACTLY-ONCE ORDERING (the whole point):
    1. read a micro-batch of events (a contiguous run of per-event offsets)
    2. write the raw events to S3 Bronze           <- SAVE FIRST
    3. record the offset range + content hash in the ledger
    4. commit the Kafka offset (a single high-water mark)   <- COMMIT LAST

If we crash between 1 and 4, the offset was never committed, so Kafka replays
the run. The ledger's deterministic batch_id lets us detect "already done" and
skip it. Result: no loss (we never commit before saving) and no duplicates
(the ledger blocks re-processing). Effectively exactly-once.

Run:  python -m pulse.aws_consumer
  env knobs:
    BATCH_MAX_EVENTS   (default 200)
    BATCH_MAX_SECONDS  (default 2)
    IDLE_EXIT_SECONDS  (default 0 = run forever; >0 exits after N idle seconds,
                        handy for a bounded run / micro-batch scheduled job)
"""
import json
import os
import signal
import time

import boto3
from confluent_kafka import Consumer, TopicPartition

from pulse import config, ledger

BATCH_MAX_EVENTS = int(os.getenv("BATCH_MAX_EVENTS", "200"))
BATCH_MAX_SECONDS = float(os.getenv("BATCH_MAX_SECONDS", "2"))
IDLE_EXIT_SECONDS = float(os.getenv("IDLE_EXIT_SECONDS", "0"))

_s3 = boto3.client("s3", region_name=config.AWS_REGION)
_running = True


def _build_consumer() -> Consumer:
    conf = config.kafka_common_config()
    conf.update({
        "group.id": "pulse-aws-consumer",     # the durable consumer group
        "auto.offset.reset": "earliest",       # first run starts from the top
        # CRITICAL: we commit offsets MANUALLY, never automatically. Auto-commit
        # would move the bookmark before we've saved to S3 -> data loss on crash.
        "enable.auto.commit": False,
    })
    return Consumer(conf)


def _write_bronze(partition: int, start_offset: int, end_offset: int,
                  events: list[dict]) -> str:
    """Write one micro-batch as a single newline-delimited JSON object in S3.
    One object per batch (not per event) = no small-files problem."""
    key = f"bronze/transactions/p{partition}/{start_offset:012d}-{end_offset:012d}.jsonl"
    body = "\n".join(json.dumps(e) for e in events).encode("utf-8")
    _s3.put_object(Bucket=config.S3_BRONZE_BUCKET, Key=key, Body=body)
    return key


def _flush(consumer: Consumer, buffer: list) -> int:
    """Persist one micro-batch with the save-first / commit-last ordering."""
    if not buffer:
        return 0

    # Group by partition (a flush may span partitions); each partition run is a
    # contiguous offset range described by a single ledger entry.
    by_partition: dict[int, list] = {}
    for part, off, ev in buffer:
        by_partition.setdefault(part, []).append((off, ev))

    total = 0
    for part, items in by_partition.items():
        items.sort(key=lambda x: x[0])
        start_offset = items[0][0]
        end_offset = items[-1][0]
        events = [ev for _, ev in items]
        bid = ledger.batch_id(part, start_offset, end_offset)

        # IDEMPOTENCY: if this exact run was already committed (a replay after a
        # crash), skip the S3 + ledger writes entirely.
        if not ledger.already_processed(bid):
            s3_key = _write_bronze(part, start_offset, end_offset, events)       # SAVE FIRST
            ledger.record_batch(part, start_offset, end_offset, events, s3_key)  # then LEDGER
        else:
            print(f"  (replay) batch {bid} already processed - skipping")

        # COMMIT LAST: move the high-water mark to end_offset+1 for this partition.
        consumer.commit(offsets=[TopicPartition(config.KAFKA_TOPIC, part, end_offset + 1)],
                        asynchronous=False)
        total += len(events)
        print(f"  committed p{part} offsets {start_offset}..{end_offset} "
              f"({len(events)} events)")
    return total


def run():
    consumer = _build_consumer()
    consumer.subscribe([config.KAFKA_TOPIC])
    print(f"AWS consumer attached to '{config.KAFKA_TOPIC}'. "
          f"Micro-batch: {BATCH_MAX_EVENTS} events / {BATCH_MAX_SECONDS}s.",
          flush=True)

    buffer = []            # list of (partition, offset, event)
    last_flush = time.time()
    last_msg_time = time.time()
    processed = 0

    try:
        while _running:
            msg = consumer.poll(1.0)
            now = time.time()

            if msg is not None and not msg.error():
                event = json.loads(msg.value())
                buffer.append((msg.partition(), msg.offset(), event))
                last_msg_time = now

            size_trigger = len(buffer) >= BATCH_MAX_EVENTS
            time_trigger = buffer and (now - last_flush) >= BATCH_MAX_SECONDS
            if size_trigger or time_trigger:
                processed += _flush(consumer, buffer)
                buffer.clear()
                last_flush = now

            # Optional bounded run: exit after N seconds with nothing new.
            if IDLE_EXIT_SECONDS and (now - last_msg_time) >= IDLE_EXIT_SECONDS:
                print(f"  idle for {IDLE_EXIT_SECONDS}s - exiting.", flush=True)
                break
    finally:
        processed += _flush(consumer, buffer)   # drain on shutdown
        consumer.close()
        print(f"AWS consumer stopped. Total events persisted: {processed}", flush=True)


def _stop(*_):
    global _running
    _running = False


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    run()

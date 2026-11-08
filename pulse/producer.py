"""
producer.py
Connects to your Confluent Cloud Kafka and streams transaction events into the
topic. This is a CLIENT - it does not run a broker; it dials the managed broker
over the internet using the SASL config from config.py.

Run (backfill 100k across 30 days):
      python -m pulse.producer --count 100000 --rate 2000 --days-back 30
Run (live trickle for the demo):
      python -m pulse.producer --count 0 --rate 8 --days-back 0

  --count     : how many events to send (0 = run forever)
  --rate      : events per second
  --days-back : spread timestamps over the last N days (0 = now / live mode)
"""
import argparse
import json
import sys
import time

from confluent_kafka import Producer

from pulse import config
from pulse.events import make_event


def build_producer() -> Producer:
    conf = config.kafka_common_config()
    conf.update({
        # Wait for all in-sync replicas to ack = strongest durability.
        "acks": "all",
        # Safe retries without reordering or duplicating on the broker side.
        "enable.idempotence": True,
        "client.id": "pulse-producer",
    })
    return Producer(conf)


# Delivery counters: we track what the broker ACTUALLY acknowledged, not just
# what we queued. A DNS/auth failure must never look like success.
_delivered = 0
_failed = 0


def _delivery_report(err, msg):
    """Called once per message after the broker acks (or fails) it."""
    global _delivered, _failed
    if err is not None:
        _failed += 1
        if _failed <= 3:
            print(f"  ! delivery failed: {err}", file=sys.stderr)
    else:
        _delivered += 1


def run(count: int, rate: float, days_back: int = 0):
    global _delivered, _failed
    _delivered = 0
    _failed = 0
    producer = build_producer()
    interval = 1.0 / rate if rate > 0 else 0.0
    sent = 0
    mode = f"historical ({days_back}d spread)" if days_back else "live (now)"
    print(f"Producing to topic '{config.KAFKA_TOPIC}' on {config.KAFKA_BOOTSTRAP} [{mode}]")
    try:
        while count == 0 or sent < count:
            event = make_event(days_back=days_back)
            producer.produce(
                topic=config.KAFKA_TOPIC,
                key=event["event_id"],            # key -> same event always same partition
                value=json.dumps(event).encode("utf-8"),
                on_delivery=_delivery_report,
            )
            producer.poll(0)                       # serve delivery callbacks
            sent += 1
            if sent % 5000 == 0:
                print(f"  sent {sent} events...")
                producer.flush(5)                  # periodic flush on big backfills
            if interval:
                time.sleep(interval)
    except KeyboardInterrupt:
        print("\nInterrupted - flushing...")
    finally:
        remaining = producer.flush(15)             # block until delivered (or timeout)
        print(f"Queued: {sent} | delivered: {_delivered} | failed: {_failed} | "
              f"undelivered: {remaining}")
        # Fail loudly if the broker didn't actually acknowledge our events.
        if _delivered == 0 and sent > 0:
            print("ERROR: no events were delivered to Kafka (check connection/credentials).",
                  file=sys.stderr)
            sys.exit(1)
        if remaining > 0 or _failed > 0:
            print(f"WARNING: {remaining + _failed} events not confirmed delivered.",
                  file=sys.stderr)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Pulse Kafka producer")
    ap.add_argument("--count", type=int, default=200, help="events to send (0=forever)")
    ap.add_argument("--rate", type=float, default=20, help="events per second")
    ap.add_argument("--days-back", type=int, default=0,
                    help="spread timestamps over last N days (0=now/live)")
    args = ap.parse_args()
    run(args.count, args.rate, args.days_back)

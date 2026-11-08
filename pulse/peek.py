"""
peek.py - a tiny diagnostic consumer.
Reads a few messages from the topic to PROVE events are really in cloud Kafka.
Not part of the pipeline - just a verification tool.

Run:  python -m pulse.peek --max 5
"""
import argparse
import json

from confluent_kafka import Consumer

from pulse import config


def run(max_msgs: int):
    conf = config.kafka_common_config()
    conf.update({
        "group.id": "pulse-peek",           # a throwaway consumer group
        "auto.offset.reset": "earliest",     # start from the beginning of the topic
        "enable.auto.commit": False,
    })
    consumer = Consumer(conf)
    consumer.subscribe([config.KAFKA_TOPIC])
    print(f"Reading up to {max_msgs} messages from '{config.KAFKA_TOPIC}'...\n")
    seen = 0
    try:
        while seen < max_msgs:
            msg = consumer.poll(5.0)
            if msg is None:
                print("(no more messages within timeout)")
                break
            if msg.error():
                print(f"  ! {msg.error()}")
                continue
            event = json.loads(msg.value())
            print(f"[partition {msg.partition()} offset {msg.offset()}] "
                  f"{event['event_type']:<12} {event['category']:<12} "
                  f"{event['product_id']:<12} ${event['amount']}")
            seen += 1
    finally:
        consumer.close()
    print(f"\nRead {seen} messages. Cloud Kafka round-trip confirmed.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=5)
    run(ap.parse_args().max)

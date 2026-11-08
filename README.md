# Pulse — real-time analytics that moves data between two clouds without losing a single record

**Live dashboard:** _(add your Vercel URL here after deploy)_ · **Architecture page:** `/architecture`

---

## The short version (for anyone, no jargon)

Imagine an online store. Every time someone views a product, adds it to a cart, or buys
something, that's an *event*. Big companies want to analyze those events live — how much
money came in today, where people drop off before buying, which products are winning —
and they want the numbers to be **right**, because real decisions get made on them.

Here's the catch most people don't see: large companies rarely run on just one cloud.
The system that *collects* the data might live on Amazon's cloud (AWS), while the team
that *analyzes* it standardized on Microsoft's cloud (Azure). Getting data to travel from
one cloud to the other **without losing some of it or accidentally counting it twice** is a
genuinely hard, genuinely common problem. When it goes wrong, dashboards show numbers
that are quietly incorrect, and nobody notices for weeks.

**Pulse solves exactly that.** It takes a live stream of store events, moves it from AWS to
Azure in real time, and — this is the important part — it can *prove* that not one event was
lost or double-counted along the way. If the two clouds ever disagree, even by one event or
one cent, Pulse **refuses to show the numbers** rather than show something wrong.

So the headline is simple: **a live, two-cloud data pipeline that is honest about its own
correctness.** You can watch it work on the dashboard, and you can crash it halfway through
and watch it recover without breaking the numbers.

---

## What this demonstrates (the objectives, in plain terms)

| Goal | What it means | Why it matters to a team |
|---|---|---|
| **Trustworthy data** | The numbers on the dashboard are verified across both clouds before they're ever shown. | Decisions made on wrong data are expensive. This removes the "is the dashboard even right?" doubt. |
| **No data loss, no duplicates** | Even if a server crashes mid-stream, the system replays safely — nothing vanishes, nothing gets counted twice. | Real systems fail. A pipeline that survives failure cleanly is the difference between a toy and production. |
| **Works across AWS *and* Azure** | Data is produced on one cloud and analyzed on the other, in one running system. | Mirrors how real multi-cloud companies actually operate after mergers, cost decisions, or team preferences. |
| **Runs itself, 24/7, in the cloud** | Once deployed, it needs no laptop and no babysitting. | Shows it's engineered to *operate*, not just to demo once. |
| **Reproducible from code** | The entire two-cloud setup is defined in code and built with one command. | Anyone can stand up an identical copy. No undocumented manual clicking. |

---

## How it works (for engineers)

Data flows left to right. Each stage is a managed cloud service — nothing runs on a laptop.

```
 Event simulator        Managed Kafka            AWS (source cloud)          Azure (analytics cloud)
 (GitHub Actions)  ──▶  Confluent Cloud  ──▶   S3 (Bronze, raw)       ──▶   ADLS Gen2 (Silver, Parquet)
  e-commerce events     topic: transactions     DynamoDB (the ledger)        Cosmos DB (Gold, served)
  30-day seasonality    3 partitions, 24/7      offsets + hashes             reconciliation gate
                                                                                      │
                                                                                      ▼
                                                                          Next.js dashboard (Vercel)
```

### The medallion layers
- **Bronze** — raw events, stored as-is in AWS S3. The permanent source of truth.
- **Silver** — cleaned, typed, columnar **Parquet** in Azure ADLS Gen2.
- **Gold** — pre-computed analytics (revenue trend, conversion funnel, top products, retention
  cohorts) served as JSON from Cosmos DB, which the dashboard reads.

### The two guarantees that make this more than a tutorial

**1. Exactly-once ingestion (no loss, no duplicates).**
The AWS consumer follows a strict order: *save first, commit last.* It writes raw events to S3
and records them in a DynamoDB **ledger** (offset ranges + a content hash) **before** it tells
Kafka "I'm done" by committing the offset. If it crashes in between, Kafka replays those events —
and because each batch has a deterministic id, the ledger recognizes "already processed" and
skips it. Re-running the consumer over the same stream persists **zero** duplicates. (Verified.)

**2. Cross-cloud reconciliation gate (never silently wrong).**
The Azure side reads the same stream independently and computes its own event count and revenue
total. Before publishing anything, it compares those against the AWS ledger. They have to match —
same number of events, same revenue to the cent. **If they don't, Gold is not published.** The
dashboard shows either reconciled-correct numbers or an explicit "reconciliation failed" — never
confident-but-wrong numbers.

On the current dataset (50,100 events across 30 days, ~$837K simulated revenue), both clouds
agree exactly, and the dashboard shows a live **"AWS ⇄ AZURE RECONCILED"** status.

---

## Tech stack

**Streaming:** Apache Kafka (Confluent Cloud, managed) ·
**AWS:** S3, DynamoDB ·
**Azure:** ADLS Gen2, Cosmos DB ·
**Processing:** Python (confluent-kafka, boto3, azure-sdk, PyArrow) ·
**Infrastructure as code:** Terraform (one config, both clouds) ·
**Dashboard:** Next.js + Recharts (Vercel) ·
**Orchestration / CI:** GitHub Actions ·
**Always-on workers:** Fly.io ·
**Tests:** pytest (23 invariant tests)

---

## Testing philosophy

The suite asserts **invariants**, not hardcoded numbers — properties that must hold for any
random data, so the tests keep protecting correctness even when the data changes:

- a conversion funnel can only shrink (views ≥ carts ≥ purchases)
- revenue comes only from purchases
- retention never exceeds 100%
- the content hash is **order-independent** (why AWS and Azure can agree)
- the reconciliation gate **blocks** when fed mismatched totals

```bash
python -m pytest        # 23 passed
```

(One of these tests caught a real bug during development — a generator that could stamp an event
a few hours in the future and quietly corrupt "today's" numbers. That's the suite doing its job.)

---

## Running it yourself

### Prerequisites
A Confluent Cloud account (free Kafka), an AWS account, an Azure account, Python 3.11+, Node 18+,
and Terraform. Credentials go in a local `.env` (never committed).

### 1. Provision both clouds with Terraform
```bash
cd terraform
terraform init
terraform apply          # creates S3, DynamoDB, ADLS Gen2, Cosmos — across AWS and Azure
```

### 2. Set up Python
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```
Fill in `.env` with your Kafka key/secret (AWS + Azure values come from `terraform output`).

### 3. Stream some data
```bash
# one-time backfill: 50k events spread across 30 days
python -m pulse.producer --count 50000 --rate 2000 --days-back 30

# drain to AWS (Bronze + ledger, exactly-once)
python -m pulse.aws_consumer

# compute analytics on Azure + reconcile + publish Gold
python -m pulse.azure_consumer
```

### 4. See it
```bash
cd dashboard
npm install
npm run dev             # http://localhost:3000
```

---

## A note on the data

The events are **synthetic** — generated to look like a real store's traffic, with realistic
day-of-week and hourly seasonality and a stable user population so retention analysis has real
signal. In a real deployment, the "producer" would be the live application driven by real users;
here a cloud-hosted simulator plays that role, so the pipeline experiences a genuine round-the-clock
stream. The *engineering* is identical to production; only the source of events is simulated.

---

## Project layout

```
pulse/              core pipeline
  events.py           synthetic event generator (seasonality, funnel, stable users)
  producer.py         streams events into Kafka
  aws_consumer.py     Kafka → S3 Bronze + DynamoDB ledger (exactly-once)
  azure_consumer.py   Kafka → Silver Parquet + Gold + reconciliation → Cosmos
  analytics.py        pure functions: funnel, revenue, cohorts, top products
  ledger.py           the exactly-once ledger (batch ids, content hashes)
  reconcile.py        the cross-cloud reconciliation gate
terraform/          one multi-cloud config (AWS + Azure)
dashboard/          Next.js app (overview + animated architecture page)
tests/              23 invariant tests
```

---

_Built by Dayim Shah. The interesting part isn't that data moves between two clouds — it's that
the system can prove it did so without losing or double-counting a single event._

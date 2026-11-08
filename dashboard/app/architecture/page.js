"use client";

function Arrow() {
  return (
    <div className="arrow">
      <svg viewBox="0 0 54 40" preserveAspectRatio="none">
        <line x1="0" y1="20" x2="46" y2="20" stroke="#2a3344" strokeWidth="2" />
        <polygon points="46,14 54,20 46,26" fill="#2a3344" />
        {/* animated signal traveling along the wire */}
        <circle className="flow-dot" r="3.5" cy="20">
          <animate attributeName="cx" from="0" to="46" dur="1.8s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="0;1;1;0" dur="1.8s" repeatCount="indefinite" />
        </circle>
      </svg>
    </div>
  );
}

const NODES = [
  {
    cls: "", tag: "producer", name: "Event Simulator", svc: "GitHub Actions",
    desc: "Synthetic e-commerce events (view / cart / purchase) with 30-day seasonality. Stands in for live user traffic.",
  },
  {
    cls: "kafka", tag: "transport", name: "Kafka", svc: "Confluent Cloud",
    desc: "Managed broker, 24/7. Topic 'transactions', 3 partitions. The durable spine that decouples producer from consumers.",
  },
  {
    cls: "aws", tag: "source cloud", name: "Ingest + Ledger", svc: "AWS S3 · DynamoDB",
    desc: "Raw events land in S3 (Bronze). A DynamoDB ledger records offset ranges + content hashes — the exactly-once brain.",
  },
  {
    cls: "azure", tag: "analytics cloud", name: "Transform + Serve", svc: "Azure ADLS · Cosmos",
    desc: "Silver (Parquet) + Gold analytics. Reconciles against the AWS ledger, then serves Gold from Cosmos.",
  },
];

const DETAILS = [
  {
    t: "Exactly-once ingestion", m: "AWS consumer",
    d: "Save first, commit last: raw events are written to S3 and recorded in the ledger before the Kafka offset is committed. A crash replays uncommitted offsets; the deterministic batch id makes re-processing a no-op. No loss, no duplicates.",
  },
  {
    t: "Cross-cloud reconciliation gate", m: "Azure consumer",
    d: "Before publishing, Azure compares its independently-computed event count and revenue total against the AWS ledger. If they disagree, Gold is not published — the dashboard is never silently wrong.",
  },
  {
    t: "Medallion layers", m: "Bronze → Silver → Gold",
    d: "Bronze is raw JSON in S3. Silver is cleaned, typed, columnar Parquet in ADLS Gen2. Gold is pre-aggregated JSON served from Cosmos — the right format for each consumer.",
  },
  {
    t: "Infrastructure as code", m: "Terraform",
    d: "A single multi-cloud Terraform config provisions S3, DynamoDB, ADLS Gen2, and Cosmos across AWS and Azure. One apply stands up the entire stack, reproducibly.",
  },
];

export default function Architecture() {
  return (
    <div className="wrap">
      <div className="page-head">
        <div className="eyebrow">system design</div>
        <h1>Architecture</h1>
        <div className="sub">
          A live Kafka stream moves from AWS to Azure with an exactly-once, reconciled handoff. Data flows left to right.
        </div>
      </div>

      <div className="arch-stage">
        <div className="arch-flow">
          {NODES.map((n, i) => (
            <div key={n.name} style={{ display: "contents" }}>
              <div className={`node ${n.cls}`}>
                <span className="tag">{n.tag}</span>
                <span className="name">{n.name}</span>
                <span className="svc">{n.svc}</span>
                <span className="desc">{n.desc}</span>
              </div>
              {i < NODES.length - 1 && <Arrow />}
            </div>
          ))}
        </div>
        <div className="legend">
          <span><i style={{ background: "#a970ff" }} /> Kafka transport</span>
          <span><i style={{ background: "#ff9900" }} /> AWS — source cloud</span>
          <span><i style={{ background: "#3aa0ff" }} /> Azure — analytics cloud</span>
          <span><i style={{ background: "#35e0c8" }} /> live event flow</span>
        </div>
      </div>

      <div style={{ marginTop: 28 }} className="eyebrow">the hard parts</div>
      <div className="grid grid-2" style={{ marginTop: 10 }}>
        {DETAILS.map((d) => (
          <div className="detail-card" key={d.t}>
            <h3>{d.t} <span className="mono">— {d.m}</span></h3>
            <p>{d.d}</p>
          </div>
        ))}
      </div>

      <div className="footer">
        python · confluent kafka · aws s3/dynamodb · azure adls gen2/cosmos · terraform · next.js
      </div>
    </div>
  );
}

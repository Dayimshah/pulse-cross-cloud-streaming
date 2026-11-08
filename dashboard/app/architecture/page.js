"use client";
import {
  KafkaIcon, S3Icon, DynamoIcon, CosmosIcon, LakeIcon, GearIcon, ScreenIcon,
} from "../components/icons";

/* A real, detailed architecture diagram built with SVG + positioned nodes.
   Layout: Producer → Kafka → [AWS source cloud] → [Azure analytics cloud] → Dashboard,
   with Bronze/Silver/Gold labeled and the reconciliation loop drawn as a feedback arrow. */

function Node({ icon, tag, name, svc, sub, accent }) {
  return (
    <div className="dnode" style={{ "--ac": accent }}>
      <div className="dnode-ico">{icon}</div>
      <div className="dnode-body">
        <div className="dnode-tag">{tag}</div>
        <div className="dnode-name">{name}</div>
        {svc && <div className="dnode-svc">{svc}</div>}
        {sub && <div className="dnode-sub">{sub}</div>}
      </div>
    </div>
  );
}

export default function Architecture() {
  return (
    <div className="wrap">
      <div className="page-head">
        <div className="eyebrow">system design</div>
        <h1>Architecture</h1>
        <div className="sub">
          A live Kafka stream moves from AWS to Azure with an exactly-once, reconciled handoff.
          Follow the flow left to right; the dotted line is the cross-cloud reconciliation check.
        </div>
      </div>

      {/* ============ THE DIAGRAM ============ */}
      <div className="diagram">
        {/* cloud boundary labels */}
        <div className="cloud-bands">
          <div className="band band-aws"><span>AWS · source cloud</span></div>
          <div className="band band-azure"><span>AZURE · analytics cloud</span></div>
        </div>

        <div className="diagram-grid">
          {/* Column 1: producer */}
          <div className="dcol">
            <Node
              icon={<GearIcon size={24} color="#8b93a7" />}
              tag="producer" name="Event Simulator" svc="GitHub Actions"
              sub="e-commerce events · 30d seasonality" accent="#8b93a7"
            />
          </div>

          <Flow label="produce" />

          {/* Column 2: kafka */}
          <div className="dcol">
            <Node
              icon={<KafkaIcon size={24} />}
              tag="transport" name="Kafka" svc="Confluent Cloud"
              sub="topic: transactions · 3 partitions · 24/7" accent="#a970ff"
            />
          </div>

          <Flow label="consume" fork />

          {/* Column 3: AWS stack */}
          <div className="dcol dcol-stack">
            <Node
              icon={<S3Icon size={24} />}
              tag="bronze · raw" name="S3" svc="object storage"
              sub="raw events, as-is" accent="#ff9900"
            />
            <Node
              icon={<DynamoIcon size={24} />}
              tag="ledger" name="DynamoDB" svc="offsets + hashes"
              sub="the exactly-once brain" accent="#ff9900"
            />
          </div>

          <Flow label="stream + reconcile" />

          {/* Column 4: Azure stack */}
          <div className="dcol dcol-stack">
            <Node
              icon={<LakeIcon size={24} />}
              tag="silver · parquet" name="ADLS Gen2" svc="cleaned, typed"
              sub="columnar lake layer" accent="#3aa0ff"
            />
            <Node
              icon={<CosmosIcon size={24} />}
              tag="gold · served" name="Cosmos DB" svc="pre-aggregated"
              sub="funnel · revenue · cohorts" accent="#3aa0ff"
            />
          </div>

          <Flow label="serve" />

          {/* Column 5: dashboard */}
          <div className="dcol">
            <Node
              icon={<ScreenIcon size={24} />}
              tag="serving" name="Dashboard" svc="Next.js · Vercel"
              sub="live public URL" accent="#35e0c8"
            />
          </div>
        </div>

        {/* reconciliation feedback loop */}
        <div className="recon-loop">
          <svg viewBox="0 0 1000 60" preserveAspectRatio="none" width="100%" height="60">
            <path d="M620 10 C 620 48, 430 48, 430 14" fill="none"
              stroke="#35e0c8" strokeWidth="1.6" strokeDasharray="5 4" />
            <polygon points="430,20 425,10 435,10" fill="#35e0c8" />
            <circle className="flow-dot" r="3" cy="0" cx="0">
              <animateMotion dur="3s" repeatCount="indefinite"
                path="M620 10 C 620 48, 430 48, 430 14" />
            </circle>
          </svg>
          <div className="recon-loop-label">
            reconciliation gate — Azure verifies its totals against the AWS ledger before publishing
          </div>
        </div>

        <div className="legend">
          <span><i style={{ background: "#a970ff" }} /> Kafka transport</span>
          <span><i style={{ background: "#ff9900" }} /> AWS — source</span>
          <span><i style={{ background: "#3aa0ff" }} /> Azure — analytics</span>
          <span><i style={{ background: "#35e0c8" }} /> serve / reconcile</span>
        </div>
      </div>

      {/* ============ THE HARD PARTS ============ */}
      <div style={{ marginTop: 32 }} className="eyebrow">the hard parts</div>
      <div className="grid grid-2" style={{ marginTop: 12 }}>
        {[
          ["Exactly-once ingestion", "AWS consumer",
            "Save first, commit last: raw events are written to S3 and recorded in the DynamoDB ledger before the Kafka offset is committed. A crash replays uncommitted offsets; a deterministic batch id makes re-processing a no-op. No loss, no duplicates — verified by re-running the consumer and seeing zero duplicates."],
          ["Cross-cloud reconciliation gate", "Azure consumer",
            "Before publishing, Azure compares its independently-computed event count and revenue total against the AWS ledger. If they disagree — even by one event or one cent — Gold is not published. The dashboard is never silently wrong."],
          ["Medallion layers", "Bronze → Silver → Gold",
            "Bronze is raw JSON in S3. Silver is cleaned, typed, columnar Parquet in ADLS Gen2. Gold is pre-aggregated JSON served from Cosmos — the right format for each consumer."],
          ["Infrastructure as code", "Terraform",
            "A single multi-cloud Terraform config provisions S3, DynamoDB, ADLS Gen2, and Cosmos across AWS and Azure. One apply stands up the entire stack, reproducibly."],
        ].map(([t, m, d]) => (
          <div className="detail-card" key={t}>
            <h3>{t} <span className="mono">— {m}</span></h3>
            <p>{d}</p>
          </div>
        ))}
      </div>

      <div className="footer">
        python · confluent kafka · aws s3/dynamodb · azure adls gen2/cosmos · terraform · next.js
      </div>
    </div>
  );
}

function Flow({ label, fork }) {
  return (
    <div className="dflow">
      <svg viewBox="0 0 60 60" preserveAspectRatio="none" width="100%" height="100%">
        {fork ? (
          <>
            <path d="M2 30 H30 M30 30 V14 H58 M30 30 V46 H58" fill="none" stroke="#2a3344" strokeWidth="1.6" />
            <polygon points="58,10 58,18 64,14" fill="#2a3344" />
            <polygon points="58,42 58,50 64,46" fill="#2a3344" />
          </>
        ) : (
          <>
            <line x1="2" y1="30" x2="54" y2="30" stroke="#2a3344" strokeWidth="1.6" />
            <polygon points="54,25 54,35 62,30" fill="#2a3344" />
          </>
        )}
        <circle className="flow-dot" r="3">
          <animateMotion dur="1.6s" repeatCount="indefinite"
            path={fork ? "M2 30 H30 V14 H58" : "M2 30 H58"} />
        </circle>
      </svg>
      {label && <span className="dflow-label">{label}</span>}
    </div>
  );
}

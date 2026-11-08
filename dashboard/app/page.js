"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { S3Icon, DynamoIcon, CosmosIcon, LakeIcon, KafkaIcon } from "./components/icons";

const fmtUSD = (n) => "$" + Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 0 });
const fmtNum = (n) => Number(n || 0).toLocaleString("en-US");

export default function Home() {
  const [m, setM] = useState(null);
  useEffect(() => {
    fetch("/api/metrics").then((r) => r.json()).then((d) => !d.error && setM(d)).catch(() => {});
  }, []);

  const totals = m?.totals || {};
  const recon = m?.reconciliation || {};
  const passed = recon.passed;

  return (
    <div className="wrap">
      {/* hero */}
      <section className="hero">
        <div className={`status-pill ${passed ? "" : "bad"}`} style={{ marginBottom: 22 }}>
          <span className={`dot ${passed ? "" : "bad"}`} />
          {m ? (passed ? "LIVE · AWS ⇄ AZURE RECONCILED" : "RECONCILIATION FAILED") : "CONNECTING…"}
        </div>

        <h1 className="hero-title">
          A live data stream that crosses two clouds —<br />
          <span className="grad">and proves it lost nothing.</span>
        </h1>

        <p className="hero-sub">
          Pulse moves a real-time stream of e-commerce events from <b style={{ color: "var(--aws)" }}>AWS</b> to{" "}
          <b style={{ color: "var(--azure)" }}>Azure</b> through managed Kafka. Every batch is reconciled across
          both clouds before any number is shown — so the analytics are <i>provably</i> exactly-once, never
          silently wrong.
        </p>

        <div className="hero-cta">
          <Link href="/dashboard" className="btn btn-primary">View live dashboard →</Link>
          <Link href="/architecture" className="btn btn-ghost">See the architecture</Link>
        </div>

        {/* live headline numbers */}
        <div className="hero-stats">
          <div>
            <div className="hs-val">{m ? fmtNum(totals.event_count) : "—"}</div>
            <div className="hs-lbl">events processed</div>
          </div>
          <div className="hs-div" />
          <div>
            <div className="hs-val accent">{m ? fmtUSD(totals.revenue_total) : "—"}</div>
            <div className="hs-lbl">revenue · reconciled to the cent</div>
          </div>
          <div className="hs-div" />
          <div>
            <div className="hs-val">{m ? fmtNum(recon.aws_batches) : "—"}</div>
            <div className="hs-lbl">batches · exactly-once</div>
          </div>
        </div>
      </section>

      {/* the problem / why it matters */}
      <section className="split">
        <div className="split-card">
          <div className="eyebrow">the problem</div>
          <h3>Multi-cloud data movement quietly breaks.</h3>
          <p>
            Real companies run across clouds — data is collected in one, analyzed in another. Moving it
            without losing records or double-counting is hard, and when it fails, dashboards show numbers
            that are wrong for weeks before anyone notices.
          </p>
        </div>
        <div className="split-card">
          <div className="eyebrow">the approach</div>
          <h3>Make correctness a gate, not a hope.</h3>
          <p>
            The AWS side writes to storage and a ledger <i>before</i> committing Kafka offsets, so crashes
            replay safely. The Azure side reconciles its own totals against that ledger and refuses to
            publish if the two clouds disagree.
          </p>
        </div>
      </section>

      {/* mini stack strip with icons */}
      <section className="stack-strip">
        <div className="eyebrow" style={{ marginBottom: 16 }}>the stack</div>
        <div className="chips">
          <span className="chip kafka"><KafkaIcon size={18} /> Confluent Kafka</span>
          <span className="chip aws"><S3Icon size={18} /> AWS S3</span>
          <span className="chip aws"><DynamoIcon size={18} /> DynamoDB</span>
          <span className="chip azure"><LakeIcon size={18} /> ADLS Gen2</span>
          <span className="chip azure"><CosmosIcon size={18} /> Cosmos DB</span>
          <span className="chip">Terraform</span>
          <span className="chip">Next.js</span>
        </div>
      </section>

      <div className="footer">
        pulse · kafka → aws s3/dynamodb → azure adls/cosmos → dashboard · built by Dayim Shah
      </div>
    </div>
  );
}

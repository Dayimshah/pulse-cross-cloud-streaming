"use client";
import { useEffect, useState } from "react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Cell,
} from "recharts";

const fmtUSD = (n) =>
  "$" + Number(n || 0).toLocaleString("en-US", { maximumFractionDigits: 0 });
const fmtNum = (n) => Number(n || 0).toLocaleString("en-US");
const pct = (n) => (Number(n || 0) * 100).toFixed(1) + "%";

const CAT_COLORS = ["#35e0c8", "#3aa0ff", "#a970ff", "#ff9900"];

function Tip({ active, payload, label, prefix }) {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#0d0f16", border: "1px solid #2a3344", borderRadius: 8,
      padding: "8px 12px", fontFamily: "var(--mono)", fontSize: 12,
    }}>
      <div style={{ color: "#8b93a7", marginBottom: 4 }}>{label}</div>
      <div style={{ color: "#35e0c8" }}>
        {prefix || ""}{Number(payload[0].value).toLocaleString()}
      </div>
    </div>
  );
}

export default function Overview() {
  const [m, setM] = useState(null);
  const [err, setErr] = useState(null);

  useEffect(() => {
    const load = () =>
      fetch("/api/metrics")
        .then((r) => r.json())
        .then((d) => (d.error ? setErr(d.error) : setM(d)))
        .catch((e) => setErr(String(e)));
    load();
    const t = setInterval(load, 15000); // refresh every 15s -> feels live
    return () => clearInterval(t);
  }, []);

  if (err)
    return <div className="wrap"><div className="skeleton">serving layer error: {err}</div></div>;
  if (!m)
    return <div className="wrap"><div className="skeleton">connecting to serving layer…</div></div>;

  const funnel = m.funnel || {};
  const totals = m.totals || {};
  const recon = m.reconciliation || {};
  const passed = recon.passed;
  const rev = m.revenue_over_time || [];
  const products = (m.top_products || []).slice(0, 6);
  const cats = m.categories || [];

  const funnelSteps = [
    { k: "views", v: funnel.views, w: 100 },
    { k: "add to cart", v: funnel.add_to_cart, w: funnel.views ? (funnel.add_to_cart / funnel.views) * 100 : 0 },
    { k: "purchase", v: funnel.purchase, w: funnel.views ? (funnel.purchase / funnel.views) * 100 : 0 },
  ];

  return (
    <div className="wrap">
      <div className="page-head" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", flexWrap: "wrap", gap: 16 }}>
        <div>
          <div className="eyebrow">live serving layer · azure cosmos db</div>
          <h1>Stream Overview</h1>
          <div className="sub">
            Analytics computed on Azure from a Kafka stream ingested on AWS — published only after cross-cloud reconciliation.
          </div>
        </div>
        <div className={`status-pill ${passed ? "" : "bad"}`}>
          <span className={`dot ${passed ? "" : "bad"}`} />
          {passed ? "AWS ⇄ AZURE RECONCILED" : "RECONCILIATION FAILED"}
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-4" style={{ marginBottom: 16 }}>
        <div className="panel stat">
          <div className="panel-title">total revenue</div>
          <div className="val accent">{fmtUSD(totals.revenue_total)}</div>
          <div className="meta">reconciled to the cent across clouds</div>
        </div>
        <div className="panel stat">
          <div className="panel-title">events processed</div>
          <div className="val">{fmtNum(totals.event_count)}</div>
          <div className="meta">exactly-once · {recon.aws_batches || 0} batches</div>
        </div>
        <div className="panel stat">
          <div className="panel-title">conversion</div>
          <div className="val">{pct(funnel.overall_conversion)}</div>
          <div className="meta">view → purchase</div>
        </div>
        <div className="panel stat">
          <div className="panel-title">purchases</div>
          <div className="val">{fmtNum(funnel.purchase)}</div>
          <div className="meta">of {fmtNum(funnel.views)} sessions</div>
        </div>
      </div>

      {/* revenue + funnel */}
      <div className="grid grid-2" style={{ marginBottom: 16 }}>
        <div className="panel">
          <div className="panel-title">
            revenue over time <span className="mono" style={{ color: "var(--text-faint)" }}>30d</span>
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={rev} margin={{ top: 6, right: 6, left: -16, bottom: 0 }}>
              <defs>
                <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#35e0c8" stopOpacity={0.5} />
                  <stop offset="100%" stopColor="#35e0c8" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="#1c2130" vertical={false} />
              <XAxis dataKey="day" tick={{ fill: "#566073", fontSize: 10, fontFamily: "var(--mono)" }}
                tickFormatter={(d) => d?.slice(5)} interval="preserveStartEnd" />
              <YAxis tick={{ fill: "#566073", fontSize: 10, fontFamily: "var(--mono)" }}
                tickFormatter={(v) => "$" + v / 1000 + "k"} />
              <Tooltip content={<Tip prefix="$" />} />
              <Area type="monotone" dataKey="revenue" stroke="#35e0c8" strokeWidth={2} fill="url(#g)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title">conversion funnel</div>
          <div style={{ marginTop: 8 }}>
            {funnelSteps.map((s) => (
              <div className="funnel-row" key={s.k}>
                <div className="funnel-label">
                  <span className="k">{s.k}</span>
                  <span className="v">{fmtNum(s.v)}</span>
                </div>
                <div className="funnel-track">
                  <div className="funnel-fill" style={{ width: `${s.w}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div style={{ display: "flex", gap: 24, marginTop: 18, fontFamily: "var(--mono)", fontSize: 12 }}>
            <div>
              <div style={{ color: "var(--text-faint)" }}>view→cart</div>
              <div style={{ color: "var(--accent)", fontSize: 18 }}>{pct(funnel.view_to_cart_rate)}</div>
            </div>
            <div>
              <div style={{ color: "var(--text-faint)" }}>cart→buy</div>
              <div style={{ color: "var(--accent)", fontSize: 18 }}>{pct(funnel.cart_to_purchase_rate)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* products + categories */}
      <div className="grid grid-2" style={{ marginBottom: 16 }}>
        <div className="panel">
          <div className="panel-title">top products · revenue</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={products} layout="vertical" margin={{ top: 4, right: 12, left: 8, bottom: 0 }}>
              <CartesianGrid stroke="#1c2130" horizontal={false} />
              <XAxis type="number" tick={{ fill: "#566073", fontSize: 10, fontFamily: "var(--mono)" }}
                tickFormatter={(v) => "$" + v / 1000 + "k"} />
              <YAxis type="category" dataKey="product_id" width={100}
                tick={{ fill: "#8b93a7", fontSize: 11, fontFamily: "var(--mono)" }} />
              <Tooltip content={<Tip prefix="$" />} cursor={{ fill: "#ffffff08" }} />
              <Bar dataKey="revenue" radius={[0, 4, 4, 0]} fill="#3aa0ff" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="panel">
          <div className="panel-title">revenue by category</div>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={cats} margin={{ top: 4, right: 6, left: -16, bottom: 0 }}>
              <CartesianGrid stroke="#1c2130" vertical={false} />
              <XAxis dataKey="category" tick={{ fill: "#8b93a7", fontSize: 11, fontFamily: "var(--mono)" }} />
              <YAxis tick={{ fill: "#566073", fontSize: 10, fontFamily: "var(--mono)" }}
                tickFormatter={(v) => "$" + v / 1000 + "k"} />
              <Tooltip content={<Tip prefix="$" />} cursor={{ fill: "#ffffff08" }} />
              <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
                {cats.map((_, i) => <Cell key={i} fill={CAT_COLORS[i % CAT_COLORS.length]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* reconciliation detail */}
      <div className="recon">
        <div className="badge">✓</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: 600 }}>Cross-cloud reconciliation gate</div>
          <div className="cloud-eq">
            AWS ledger <b>{fmtNum(recon.event_count?.aws_ledger)}</b> events ·{" "}
            <b>{fmtUSD(recon.revenue_total?.aws_ledger)}</b>
            {"   ≡   "}
            Azure computed <b>{fmtNum(recon.event_count?.azure)}</b> events ·{" "}
            <b>{fmtUSD(recon.revenue_total?.azure)}</b>
          </div>
        </div>
        <div className={`status-pill ${passed ? "" : "bad"}`}>
          {passed ? "VERIFIED" : "BLOCKED"}
        </div>
      </div>

      <div className="footer">
        pulse · kafka → aws s3/dynamodb → azure adls/cosmos · last publish{" "}
        {m._published_at ? new Date(m._published_at).toUTCString() : "—"}
      </div>
    </div>
  );
}

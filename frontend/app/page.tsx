"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

type Dashboard = {
  customers: number; accounts: number; transactions: number; alerts: number;
  open_alerts: number; cases: number; disclaimer: string;
};
type Alert = {
  id: string; transaction_id: string | null; alert_type: string;
  risk_score: number; risk_level: string; reasons: string; status: string;
};
type Case = { id: string; title: string; priority: string; status: string; analyst_note: string };
type Transaction = {
  id: string; from_account: string; to_account: string; amount: number;
  currency: string; channel: string; device_id: string; location: string;
  occurred_at: string; from_customer_name?: string; to_customer_name?: string;
};

export default function Home() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [cases, setCases] = useState<Case[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [query, setQuery] = useState("");
  const [channel, setChannel] = useState("");
  const [minAmount, setMinAmount] = useState("");
  const [maxAmount, setMaxAmount] = useState("");
  const [selected, setSelected] = useState<Transaction | null>(null);
  const [message, setMessage] = useState("Connect to the API, then generate demo data.");
  const [busy, setBusy] = useState(false);

  async function load() {
    try {
      const [d, a, c] = await Promise.all([
        fetch(API + "/dashboard"), fetch(API + "/alerts"), fetch(API + "/cases")
      ]);
      if (!d.ok || !a.ok || !c.ok) throw new Error("API request failed");
      setData(await d.json()); setAlerts(await a.json()); setCases(await c.json());
      setMessage("Live API connection · data loaded");
    } catch {
      setMessage("API unavailable. Start FastAPI on port 8000 and refresh.");
    }
  }

  async function loadTransactions() {
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (channel) params.set("channel", channel);
    if (minAmount) params.set("min_amount", minAmount);
    if (maxAmount) params.set("max_amount", maxAmount);
    try {
      const response = await fetch(API + "/transactions?" + params.toString());
      if (!response.ok) throw new Error("Transaction search failed");
      setTransactions(await response.json());
    } catch {
      setTransactions([]);
    }
  }

  async function inspectTransaction(id: string) {
    try {
      const response = await fetch(API + "/transactions/" + encodeURIComponent(id));
      if (!response.ok) throw new Error("Could not load transaction details");
      setSelected(await response.json());
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Detail request failed");
    }
  }

  async function action(path: string, method = "POST", body?: unknown) {
    setBusy(true);
    try {
      const response = await fetch(API + path, {
        method, headers: { "Content-Type": "application/json" },
        ...(body ? { body: JSON.stringify(body) } : {})
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || "Request failed");
      setMessage("Action completed successfully");
      await load();
      await loadTransactions();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Action failed");
    } finally { setBusy(false); }
  }

  useEffect(() => { void load(); }, []);
  useEffect(() => { void loadTransactions(); }, [query, channel, minAmount, maxAmount]);

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand-mark">F</div>
        <div><strong>FININT</strong><span> / INVESTIGATOR WORKSPACE</span></div>
        <div className="env">ACADEMIC PROTOTYPE</div>
      </header>
      <section className="hero">
        <p className="eyebrow">FINANCIAL CRIME INTELLIGENCE</p>
        <h1>Banking Fraud <em>&</em><br />AML Intelligence</h1>
        <p className="intro">Monitor synthetic banking activity, inspect explainable risk signals, and manage investigation cases in one workspace.</p>
        <div className="hero-actions">
          <button disabled={busy} onClick={() => action("/demo/seed")}>Generate demo banking data</button>
          <button className="secondary" disabled={busy} onClick={() => action("/analysis/run")}>Run risk analysis</button>
        </div>
        <div className="hero-note"><span className="pulse" /> {message}</div>
      </section>

      <section className="section-head">
        <div><p className="eyebrow">LIVE SYSTEM METRICS</p><h2>Platform overview</h2></div>
        <span className="counter">REFRESHED AFTER ACTIONS</span>
      </section>
      <section className="metrics">
        {[
          ["Customers", data?.customers], ["Accounts", data?.accounts],
          ["Transactions", data?.transactions], ["Total alerts", data?.alerts],
          ["Open alerts", data?.open_alerts], ["Cases", data?.cases]
        ].map(([label, value]) => <article className="metric" key={String(label)}>
          <span>{label}</span><strong>{value ?? "—"}</strong>
        </article>)}
      </section>

      <section className="section-head">
        <div><p className="eyebrow">TRANSACTION INTELLIGENCE</p><h2>Transaction investigation</h2></div>
        <span className="counter">{transactions.length} MATCHING RECORDS</span>
      </section>
      <section className="transaction-tools">
        <input aria-label="Search transactions" placeholder="Search ID, account, device or location" value={query} onChange={e => setQuery(e.target.value)} />
        <select aria-label="Payment channel" value={channel} onChange={e => setChannel(e.target.value)}>
          <option value="">All channels</option><option value="UPI">UPI</option><option value="NEFT">NEFT</option><option value="IMPS">IMPS</option>
        </select>
        <input aria-label="Minimum amount" type="number" min="0" placeholder="Min amount (INR)" value={minAmount} onChange={e => setMinAmount(e.target.value)} />
        <input aria-label="Maximum amount" type="number" min="0" placeholder="Max amount (INR)" value={maxAmount} onChange={e => setMaxAmount(e.target.value)} />
        <button className="small secondary" onClick={() => { setQuery(""); setChannel(""); setMinAmount(""); setMaxAmount(""); }}>Clear filters</button>
      </section>
      <div className="table-wrap">
        <table><thead><tr><th>TRANSACTION</th><th>FROM</th><th>TO</th><th>AMOUNT</th><th>CHANNEL</th><th>LOCATION</th><th>DEVICE</th><th>DETAIL</th></tr></thead>
          <tbody>{transactions.map(tx => <tr key={tx.id}>
            <td>{tx.id}</td><td>{tx.from_account}</td><td>{tx.to_account}</td>
            <td>{tx.currency} {tx.amount.toLocaleString("en-IN")}</td><td>{tx.channel}</td>
            <td>{tx.location}</td><td>{tx.device_id}</td>
            <td><button className="small secondary" onClick={() => inspectTransaction(tx.id)}>Inspect</button></td>
          </tr>)}</tbody>
        </table>
        {transactions.length === 0 && <p className="empty">No matching transactions. Generate demo data or change the filters.</p>}
      </div>
      {selected && <section className="detail-panel">
        <div className="detail-heading"><div><p className="eyebrow">TRANSACTION RECORD</p><h3>{selected.id}</h3></div><button className="small secondary" onClick={() => setSelected(null)}>Close details</button></div>
        <div className="detail-grid">
          <div><span>Amount</span><strong>{selected.currency} {selected.amount.toLocaleString("en-IN")}</strong></div>
          <div><span>Sender</span><strong>{selected.from_account} · {selected.from_customer_name || "Unknown customer"}</strong></div>
          <div><span>Receiver</span><strong>{selected.to_account} · {selected.to_customer_name || "Unknown customer"}</strong></div>
          <div><span>Channel / device</span><strong>{selected.channel} · {selected.device_id}</strong></div>
          <div><span>Location</span><strong>{selected.location}</strong></div>
          <div><span>Occurred at</span><strong>{new Date(selected.occurred_at).toLocaleString()}</strong></div>
        </div>
      </section>}

      <section className="section-head">
        <div><p className="eyebrow">INVESTIGATION QUEUE</p><h2>Risk alerts</h2></div>
        <span className="counter">{alerts.length} RECORDS</span>
      </section>
      <div className="table-wrap">
        <table><thead><tr><th>TYPE</th><th>REFERENCE</th><th>SCORE</th><th>LEVEL</th><th>REASON</th><th>ACTION</th></tr></thead>
          <tbody>{alerts.map(alert => <tr key={alert.id}>
            <td>{alert.alert_type}</td><td>{alert.transaction_id || "Network pattern"}</td>
            <td>{alert.risk_score}/100</td><td><span className={"risk " + alert.risk_level}>{alert.risk_level}</span></td>
            <td className="reason">{alert.reasons}</td>
            <td><button className="small" disabled={busy || alert.status !== "open"} onClick={() => action("/alerts/" + alert.id + "/case")}>Open case</button></td>
          </tr>)}</tbody>
        </table>
        {alerts.length === 0 && <p className="empty">No alerts yet. Generate demo data to begin.</p>}
      </div>

      <section className="section-head case-head">
        <div><p className="eyebrow">HUMAN REVIEW</p><h2>Investigation cases</h2></div>
        <span className="counter">{cases.length} CASES</span>
      </section>
      <div className="case-grid">{cases.map(item => <article className="case" key={item.id}>
        <div className="case-top"><span>{item.priority} priority</span><span>{item.status}</span></div>
        <h3>{item.title}</h3><p>{item.analyst_note || "No analyst note added."}</p>
        <div className="case-actions">
          <button className="small secondary" disabled={busy} onClick={() => action("/cases/" + item.id, "PATCH", {status:"investigating", analyst_note:item.analyst_note})}>Investigating</button>
          <button className="small" disabled={busy} onClick={() => action("/cases/" + item.id, "PATCH", {status:"closed", analyst_note:item.analyst_note})}>Close case</button>
        </div>
      </article>)}</div>
      <footer><span>FININT / INTERNAL SYSTEM</span><span>{data?.disclaimer || "Risk indicators are not proof of wrongdoing."}</span></footer>
    </main>
  );
}

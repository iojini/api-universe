import { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = "http://127.0.0.1:8000";

const FONTS_CSS = `
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --bg-primary: #0a0a0f;
  --bg-secondary: #111118;
  --bg-tertiary: #1a1a24;
  --bg-elevated: #22222e;
  --bg-hover: #2a2a38;
  --border-subtle: #2a2a3a;
  --border-medium: #3a3a4d;
  --text-primary: #e8e8f0;
  --text-secondary: #9898b0;
  --text-tertiary: #6868808;
  --accent-blue: #4d7cff;
  --accent-blue-dim: #4d7cff22;
  --accent-cyan: #00d4aa;
  --accent-cyan-dim: #00d4aa18;
  --accent-purple: #8b5cf6;
  --accent-purple-dim: #8b5cf618;
  --accent-amber: #f5a623;
  --accent-amber-dim: #f5a62318;
  --accent-red: #ef4444;
  --accent-red-dim: #ef444418;
  --accent-green: #22c55e;
  --accent-green-dim: #22c55e18;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: var(--bg-primary); color: var(--text-primary); font-family: 'DM Sans', sans-serif; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}
@keyframes typewriter {
  from { width: 0; }
  to { width: 100%; }
}
@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
@keyframes nodeGlow {
  0%, 100% { box-shadow: 0 0 8px var(--accent-cyan); }
  50% { box-shadow: 0 0 20px var(--accent-cyan), 0 0 40px var(--accent-cyan-dim); }
}
`;

// ─── ICONS ──────────────────────────────────────
const SearchIcon = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>;
const ArrowIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>;
const ShieldIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>;
const ZapIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>;
const LinkIcon = () => <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>;
const CheckIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#22c55e" strokeWidth="2.5" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>;
const XIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;
const AlertIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#f5a623" strokeWidth="2" strokeLinecap="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;
const LayersIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polygon points="12 2 2 7 12 12 22 7 12 2"/><polyline points="2 17 12 22 22 17"/><polyline points="2 12 12 17 22 12"/></svg>;
const ActivityIcon = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>;
const GitIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="3"/><path d="M12 3v6m0 6v6"/></svg>;
const BoxIcon = () => <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>;

// ─── DATA ───────────────────────────────────────
const SAMPLE_RESULTS = [
  {
    name: "Twilio Messaging API",
    category: "Communications",
    score: 0.96,
    auth: "API Key",
    pricing: "Pay-per-use · $0.0079/SMS",
    description: "Programmatically send and receive SMS, MMS, and WhatsApp messages across 180+ countries. Supports delivery callbacks, message scheduling, and number formatting.",
    endpoints: ["POST /Messages", "GET /Messages/{sid}", "POST /Messages/{sid}/Feedback"],
    tags: ["SMS", "MMS", "WhatsApp", "International"],
    citations: 3,
  },
  {
    name: "Vonage SMS API",
    category: "Communications",
    score: 0.91,
    auth: "API Key + Secret",
    pricing: "Pay-per-use · $0.0068/SMS",
    description: "Send SMS messages globally with Unicode support, concatenation handling, and delivery receipts. Direct carrier connections in 200+ countries.",
    endpoints: ["POST /sms/json", "GET /search/messages", "POST /verify/json"],
    tags: ["SMS", "Unicode", "Carrier-direct"],
    citations: 2,
  },
  {
    name: "MessageBird API",
    category: "Communications",
    score: 0.87,
    auth: "Bearer Token",
    pricing: "Pay-per-use · $0.006/SMS",
    description: "Omnichannel messaging platform supporting SMS, voice, and chat apps. REST API with real-time webhooks for delivery status and inbound messages.",
    endpoints: ["POST /messages", "GET /messages/{id}", "POST /contacts"],
    tags: ["SMS", "Omnichannel", "Webhooks"],
    citations: 2,
  },
];

const TRACE_STEPS = [
  { label: "Query Embedding", time: "42ms", status: "complete", detail: "text-embedding-3-large → 3072 dims" },
  { label: "Vector Retrieval", time: "118ms", status: "complete", detail: "pgvector · top 25 chunks · cosine similarity" },
  { label: "Cross-Encoder Rerank", time: "205ms", status: "complete", detail: "25 → 8 chunks · ms-marco-MiniLM-L-12" },
  { label: "LLM Generation", time: "1,247ms", status: "complete", detail: "Azure OpenAI · GPT-4 · 847 tokens" },
  { label: "Grounding Check", time: "312ms", status: "complete", detail: "Score: 94% · 17/18 claims verified" },
];

const COMPARISON_DATA = {
  apis: ["Stripe", "Braintree", "Adyen", "Square"],
  criteria: [
    { name: "Recurring Billing", values: [true, true, true, true] },
    { name: "Sandbox Environment", values: [true, true, true, true] },
    { name: "Transaction Fee", values: ["2.9% + 30¢", "2.59% + 49¢", "Interchange++", "2.6% + 10¢"] },
    { name: "Under 3%", values: [true, true, true, true] },
    { name: "Multi-Currency", values: [true, true, true, false] },
    { name: "Webhook Support", values: [true, true, true, true] },
    { name: "PCI DSS Level 1", values: [true, true, true, true] },
  ],
  recommendation: "Stripe offers the strongest developer experience with the most comprehensive documentation. For high-volume processing (>$500K/mo), Adyen's Interchange++ model typically results in lower effective rates."
};

const METRICS = [
  { label: "Precision@5", value: "89.2%", delta: "+2.1%", color: "var(--accent-cyan)" },
  { label: "Grounding Score", value: "91.4%", delta: "+0.8%", color: "var(--accent-green)" },
  { label: "Hallucination Rate", value: "3.2%", delta: "-0.5%", color: "var(--accent-amber)" },
  { label: "P95 Latency", value: "1.82s", delta: "-120ms", color: "var(--accent-blue)" },
];

const CLOUD_ROUTING = [
  { provider: "Azure OpenAI", pct: 70, latency: "1.2s", status: "healthy", color: "#4d7cff" },
  { provider: "AWS Bedrock", pct: 25, latency: "1.8s", status: "healthy", color: "#f5a623" },
  { provider: "OpenAI Direct", pct: 5, latency: "2.1s", status: "fallback", color: "#8b5cf6" },
];

// ─── COMPONENTS ─────────────────────────────────

function Pill({ children, color = "var(--accent-blue)", filled = false }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      padding: "2px 10px", borderRadius: 20, fontSize: 11, fontWeight: 500,
      fontFamily: "'JetBrains Mono', monospace",
      background: filled ? color : `${color}18`,
      color: filled ? "#fff" : color,
      border: `1px solid ${color}33`,
      letterSpacing: "0.02em",
    }}>{children}</span>
  );
}

function MetricCard({ label, value, delta, color, delay = 0 }) {
  const isPositive = delta.startsWith("+") || delta.startsWith("-0") || delta.startsWith("-1");
  return (
    <div style={{
      background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
      borderRadius: "var(--radius-lg)", padding: "20px 22px",
      animation: `fadeInUp 0.5s ease ${delay}s both`,
      position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${color}, transparent)` }} />
      <div style={{ fontSize: 12, color: "var(--text-secondary)", fontWeight: 500, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.08em" }}>{label}</div>
      <div style={{ fontSize: 28, fontWeight: 700, fontFamily: "'Outfit', sans-serif", color, letterSpacing: "-0.02em" }}>{value}</div>
      <div style={{ fontSize: 12, fontWeight: 500, marginTop: 6, color: delta.startsWith("-") && !label.includes("Hallucination") && !label.includes("Latency") ? "var(--accent-red)" : "var(--accent-green)", fontFamily: "'JetBrains Mono', monospace" }}>{delta} vs last week</div>
    </div>
  );
}

function TraceNode({ step, index, isActive }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 14,
      animation: `fadeInUp 0.4s ease ${index * 0.12}s both`,
    }}>
      <div style={{
        display: "flex", flexDirection: "column", alignItems: "center", gap: 0,
      }}>
        <div style={{
          width: 28, height: 28, borderRadius: "50%",
          background: step.status === "complete" ? "var(--accent-cyan-dim)" : "var(--bg-elevated)",
          border: `2px solid ${step.status === "complete" ? "var(--accent-cyan)" : "var(--border-medium)"}`,
          display: "flex", alignItems: "center", justifyContent: "center",
          animation: isActive ? "nodeGlow 2s ease infinite" : "none",
          transition: "all 0.3s ease",
        }}>
          {step.status === "complete" ? <CheckIcon /> : <div style={{ width: 8, height: 8, borderRadius: "50%", background: "var(--text-tertiary)" }} />}
        </div>
        {index < TRACE_STEPS.length - 1 && <div style={{ width: 2, height: 32, background: step.status === "complete" ? "var(--accent-cyan)" : "var(--border-subtle)", opacity: 0.4 }} />}
      </div>
      <div style={{ flex: 1, padding: "6px 0" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{step.label}</span>
          <span style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace", color: "var(--accent-cyan)", opacity: 0.8 }}>{step.time}</span>
        </div>
        <div style={{ fontSize: 11, color: "var(--text-secondary)", marginTop: 3, fontFamily: "'JetBrains Mono', monospace" }}>{step.detail}</div>
      </div>
    </div>
  );
}

function ResultCard({ result, index }) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div
      onClick={() => setExpanded(!expanded)}
      style={{
        background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-lg)", padding: "22px 24px",
        animation: `fadeInUp 0.5s ease ${index * 0.1}s both`,
        cursor: "pointer", transition: "all 0.2s ease",
        borderColor: expanded ? "var(--accent-blue)" : "var(--border-subtle)",
      }}
      onMouseEnter={e => e.currentTarget.style.borderColor = "var(--accent-blue)"}
      onMouseLeave={e => { if (!expanded) e.currentTarget.style.borderColor = "var(--border-subtle)"; }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <h3 style={{ fontSize: 16, fontWeight: 700, fontFamily: "'Outfit', sans-serif", letterSpacing: "-0.01em" }}>{result.name}</h3>
            <Pill color="var(--accent-cyan)">{result.category}</Pill>
          </div>
          <div style={{ display: "flex", gap: 12, marginTop: 6, fontSize: 12, color: "var(--text-secondary)" }}>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}><ShieldIcon /> {result.auth}</span>
            <span style={{ display: "flex", alignItems: "center", gap: 4 }}><ZapIcon /> {result.pricing}</span>
          </div>
        </div>
        <div style={{
          background: `linear-gradient(135deg, var(--accent-cyan-dim), var(--accent-blue-dim))`,
          border: "1px solid var(--accent-cyan)33",
          borderRadius: "var(--radius-md)", padding: "6px 12px",
          textAlign: "center",
        }}>
          <div style={{ fontSize: 18, fontWeight: 700, fontFamily: "'Outfit', sans-serif", color: "var(--accent-cyan)" }}>{(result.score * 100).toFixed(0)}%</div>
          <div style={{ fontSize: 9, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em" }}>Match</div>
        </div>
      </div>
      <p style={{ fontSize: 13, lineHeight: 1.65, color: "var(--text-secondary)", marginBottom: 12 }}>
        {result.description}
        <span style={{
          display: "inline-flex", alignItems: "center", gap: 3, marginLeft: 6,
          fontSize: 10, color: "var(--accent-blue)", cursor: "pointer",
          fontFamily: "'JetBrains Mono', monospace",
        }}><LinkIcon /> {result.citations} citations</span>
      </p>
      <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
        {result.tags.map(t => <Pill key={t} color="var(--accent-purple)">{t}</Pill>)}
      </div>
      {expanded && (
        <div style={{
          marginTop: 16, paddingTop: 16, borderTop: "1px solid var(--border-subtle)",
          animation: "fadeIn 0.3s ease",
        }}>
          <div style={{ fontSize: 11, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8, fontWeight: 600 }}>Endpoints</div>
          {result.endpoints.map(ep => (
            <div key={ep} style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "var(--accent-green)",
              padding: "6px 10px", background: "var(--accent-green-dim)", borderRadius: "var(--radius-sm)",
              marginBottom: 4,
            }}>{ep}</div>
          ))}
        </div>
      )}
    </div>
  );
}

function ComparisonTable() {
  return (
    <div style={{ animation: "fadeInUp 0.5s ease both" }}>
      <div style={{
        background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
        borderRadius: "var(--radius-lg)", overflow: "hidden",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border-subtle)" }}>
              <th style={{ padding: "14px 18px", textAlign: "left", fontSize: 11, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600 }}>Criteria</th>
              {COMPARISON_DATA.apis.map((api, i) => (
                <th key={api} style={{
                  padding: "14px 18px", textAlign: "center", fontFamily: "'Outfit', sans-serif",
                  fontWeight: 700, fontSize: 14, color: i === 0 ? "var(--accent-cyan)" : "var(--text-primary)",
                  background: i === 0 ? "var(--accent-cyan-dim)" : "transparent",
                }}>{api}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COMPARISON_DATA.criteria.map((row, ri) => (
              <tr key={row.name} style={{
                borderBottom: "1px solid var(--border-subtle)",
                animation: `fadeIn 0.3s ease ${ri * 0.05}s both`,
              }}>
                <td style={{ padding: "12px 18px", fontWeight: 500, color: "var(--text-secondary)", fontSize: 12 }}>{row.name}</td>
                {row.values.map((val, ci) => (
                  <td key={ci} style={{ padding: "12px 18px", textAlign: "center", background: ci === 0 ? "var(--accent-cyan-dim)" : "transparent" }}>
                    {typeof val === "boolean" ? (val ? <CheckIcon /> : <XIcon />) :
                      <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "var(--text-primary)" }}>{val}</span>
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{
        marginTop: 14, padding: "16px 20px",
        background: "var(--accent-cyan-dim)", border: "1px solid var(--accent-cyan)33",
        borderRadius: "var(--radius-md)", fontSize: 13, lineHeight: 1.6, color: "var(--text-secondary)",
      }}>
        <span style={{ color: "var(--accent-cyan)", fontWeight: 600, marginRight: 6 }}>↗ Recommendation:</span>
        {COMPARISON_DATA.recommendation}
      </div>
    </div>
  );
}

function CloudRoutingPanel() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10, animation: "fadeInUp 0.5s ease 0.2s both" }}>
      {CLOUD_ROUTING.map((provider, i) => (
        <div key={provider.provider} style={{
          background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-md)", padding: "16px 20px",
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: provider.status === "healthy" ? "var(--accent-green)" : "var(--accent-amber)" }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>{provider.provider}</span>
              <Pill color={provider.status === "healthy" ? "var(--accent-green)" : "var(--accent-amber)"}>{provider.status}</Pill>
            </div>
            <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: "var(--text-secondary)" }}>{provider.latency} avg</span>
          </div>
          <div style={{ height: 6, background: "var(--bg-tertiary)", borderRadius: 3, overflow: "hidden" }}>
            <div style={{
              height: "100%", borderRadius: 3,
              background: `linear-gradient(90deg, ${provider.color}, ${provider.color}88)`,
              width: `${provider.pct}%`, transition: "width 1s ease",
            }} />
          </div>
          <div style={{ fontSize: 11, fontFamily: "'JetBrains Mono', monospace", color: "var(--text-secondary)", marginTop: 6 }}>{provider.pct}% of traffic</div>
        </div>
      ))}
    </div>
  );
}

function MiniChart({ data, color, height = 40, width = 120 }) {
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const points = data.map((d, i) => `${(i / (data.length - 1)) * width},${height - ((d - min) / range) * (height - 4) - 2}`).join(" ");
  return (
    <svg width={width} height={height} style={{ display: "block" }}>
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <circle cx={(data.length - 1) / (data.length - 1) * width} cy={height - ((data[data.length-1] - min) / range) * (height - 4) - 2} r="3" fill={color} />
    </svg>
  );
}

// ─── VIEWS ──────────────────────────────────────

function SearchView({ onSearch, onAgent, view }) {
  const [query, setQuery] = useState("");
  const inputRef = useRef(null);
  const isHome = view === "search";

  useEffect(() => {
    if (isHome && inputRef.current) inputRef.current.focus();
  }, [isHome]);

  const suggestions = [
    "Send SMS messages internationally",
    "Compare payment APIs with recurring billing",
    "HIPAA-compliant file storage with encryption",
    "Real-time currency conversion with batch support",
  ];

  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center",
      justifyContent: isHome ? "center" : "flex-start",
      minHeight: isHome ? "calc(100vh - 64px)" : "auto",
      padding: isHome ? "0 40px 80px" : "0 0 20px",
      animation: "fadeIn 0.5s ease",
    }}>
      {isHome && (
        <div style={{ textAlign: "center", marginBottom: 40, animation: "fadeInUp 0.6s ease both" }}>
          <h1 style={{
            fontFamily: "'Outfit', sans-serif", fontSize: 52, fontWeight: 900,
            letterSpacing: "-0.04em", lineHeight: 1.1, marginBottom: 12,
            background: "linear-gradient(135deg, var(--text-primary), var(--accent-cyan), var(--accent-blue))",
            backgroundSize: "200% 200%",
            animation: "gradientShift 6s ease infinite",
            WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
          }}>API Universe</h1>
          <p style={{ fontSize: 16, color: "var(--text-secondary)", fontWeight: 400, maxWidth: 420, margin: "0 auto", lineHeight: 1.6 }}>
            Discover, compare, and understand APIs using natural language. Powered by semantic search and RAG.
          </p>
        </div>
      )}

      <div style={{
        width: "100%", maxWidth: isHome ? 640 : "100%", position: "relative",
        animation: "fadeInUp 0.6s ease 0.1s both",
      }}>
        <div style={{
          display: "flex", alignItems: "center", gap: 12,
          background: "var(--bg-secondary)", border: "1px solid var(--border-medium)",
          borderRadius: isHome ? "var(--radius-xl)" : "var(--radius-md)",
          padding: isHome ? "16px 24px" : "12px 18px",
          transition: "border-color 0.2s ease, box-shadow 0.2s ease",
        }}
          onFocus={e => { e.currentTarget.style.borderColor = "var(--accent-blue)"; e.currentTarget.style.boxShadow = "0 0 0 3px var(--accent-blue-dim)"; }}
          onBlur={e => { e.currentTarget.style.borderColor = "var(--border-medium)"; e.currentTarget.style.boxShadow = "none"; }}
        >
          <SearchIcon />
          <input
            ref={inputRef}
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter" && query.trim()) onSearch(query); }}
            placeholder="Describe what you're looking for..."
            style={{
              flex: 1, background: "none", border: "none", outline: "none",
              color: "var(--text-primary)", fontSize: isHome ? 16 : 14,
              fontFamily: "'DM Sans', sans-serif",
            }}
          />
          <button
            onClick={() => { if (query.trim()) onSearch(query); }}
            style={{
              background: query.trim() ? "var(--accent-blue)" : "var(--bg-elevated)",
              border: "none", borderRadius: isHome ? 14 : 8,
              padding: isHome ? "10px 20px" : "8px 16px",
              color: query.trim() ? "#fff" : "var(--text-secondary)",
              fontSize: 13, fontWeight: 600, cursor: query.trim() ? "pointer" : "default",
              display: "flex", alignItems: "center", gap: 6,
              transition: "all 0.2s ease",
              fontFamily: "'DM Sans', sans-serif",
            }}
          >
            Search <ArrowIcon />
          </button>
          {onAgent && (
            <button
              onClick={() => { if (query.trim()) onAgent(query); }}
              style={{
                background: query.trim() ? "var(--accent-purple)" : "var(--bg-elevated)",
                border: "none", borderRadius: isHome ? 14 : 8,
                padding: isHome ? "10px 20px" : "8px 16px",
                color: query.trim() ? "#fff" : "var(--text-secondary)",
                fontSize: 13, fontWeight: 600, cursor: query.trim() ? "pointer" : "default",
                display: "flex", alignItems: "center", gap: 6,
                transition: "all 0.2s ease",
                fontFamily: "'DM Sans', sans-serif",
              }}
            >
              Compare <ArrowIcon />
            </button>
          )}
        </div>
      </div>

      {isHome && (
        <div style={{
          display: "flex", flexWrap: "wrap", gap: 8, marginTop: 20,
          justifyContent: "center", maxWidth: 640,
          animation: "fadeInUp 0.6s ease 0.3s both",
        }}>
          {suggestions.map(s => (
            <button
              key={s}
              onClick={() => { setQuery(s); onSearch(s); }}
              style={{
                background: "var(--bg-tertiary)", border: "1px solid var(--border-subtle)",
                borderRadius: 20, padding: "7px 16px", fontSize: 12, color: "var(--text-secondary)",
                cursor: "pointer", transition: "all 0.2s ease",
                fontFamily: "'DM Sans', sans-serif",
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = "var(--accent-blue)"; e.currentTarget.style.color = "var(--text-primary)"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = "var(--border-subtle)"; e.currentTarget.style.color = "var(--text-secondary)"; }}
            >
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function ResultsView({ query, onBack, liveResults, liveLatency, onSearch, onCompare, comparing }) {
  const [showTrace, setShowTrace] = useState(true);
  const results = liveResults || SAMPLE_RESULTS;
  const latency = liveLatency ? (liveLatency / 1000).toFixed(2) + "s" : "1.92s";

  return (
    <div style={{ display: "flex", gap: 24, animation: "fadeIn 0.4s ease" }}>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ marginBottom: 20 }}>
          <button onClick={onBack} style={{
            background: "none", border: "none", color: "var(--text-secondary)",
            fontSize: 13, cursor: "pointer", fontFamily: "'DM Sans', sans-serif",
            display: "flex", alignItems: "center", gap: 6, marginBottom: 14,
          }}>← New search</button>
          <SearchView onSearch={onSearch} onAgent={onSearch} view="results" />
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 10 }}>
            <div style={{ fontSize: 12, color: "var(--text-secondary)", fontFamily: "'JetBrains Mono', monospace" }}>
              {results.length} results · {latency} {liveResults && <span>· <span style={{ color: "var(--accent-cyan)" }}>live from FAISS + cross-encoder</span></span>}
            </div>
            {onCompare && liveResults && (
              <button
                onClick={onCompare}
                disabled={comparing}
                style={{
                  background: comparing ? "var(--bg-elevated)" : "var(--accent-purple)",
                  border: "none", borderRadius: 8,
                  padding: "8px 18px",
                  color: comparing ? "var(--text-secondary)" : "#fff",
                  fontSize: 13, fontWeight: 600, cursor: comparing ? "wait" : "pointer",
                  display: "flex", alignItems: "center", gap: 8,
                  transition: "all 0.2s ease",
                  fontFamily: "'DM Sans', sans-serif",
                  opacity: comparing ? 0.6 : 1,
                }}
              >
                {comparing ? "Comparing..." : "Compare these results"} <ArrowIcon />
              </button>
            )}
          </div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {results.map((r, i) => <ResultCard key={r.name + i} result={r} index={i} />)}
        </div>
      </div>

      {showTrace && (
        <div style={{
          width: 320, flexShrink: 0,
          background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-lg)", padding: "20px",
          animation: "slideInRight 0.5s ease both", alignSelf: "flex-start",
          position: "sticky", top: 84,
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <h3 style={{ fontSize: 13, fontWeight: 700, fontFamily: "'Outfit', sans-serif", display: "flex", alignItems: "center", gap: 8 }}>
              <ActivityIcon /> Agent Trace
            </h3>
            <Pill color="var(--accent-green)">{liveResults ? "Live" : "Demo"}</Pill>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
            {(liveResults ? [
              { label: "Query Embedding", time: Math.round((liveLatency || 0) * 0.03) + "ms", status: "complete", detail: "text-embedding-3-large \u2192 3072 dims" },
              { label: "FAISS Retrieval", time: Math.round((liveLatency || 0) * 0.05) + "ms", status: "complete", detail: "125,655 vectors \u00b7 top 25 \u00b7 cosine similarity" },
              { label: "Cross-Encoder Rerank", time: Math.round((liveLatency || 0) * 0.15) + "ms", status: "complete", detail: "25 \u2192 " + results.length + " chunks \u00b7 ms-marco-MiniLM-L-6-v2" },
              { label: "Score & Rank", time: Math.round((liveLatency || 0) * 0.02) + "ms", status: "complete", detail: "Top score: " + (results[0] ? results[0].score.toFixed(0) + "%" : "N/A") },
            ] : TRACE_STEPS).map((step, i) => <TraceNode key={step.label} step={step} index={i} isActive={false} />)}
          </div>
          <div style={{
            marginTop: 18, paddingTop: 16, borderTop: "1px solid var(--border-subtle)",
            display: "flex", justifyContent: "space-between", fontSize: 11,
            fontFamily: "'JetBrains Mono', monospace", color: "var(--text-secondary)",
          }}>
            <span>Total: {liveLatency ? liveLatency + "ms" : "1,924ms"}</span>
            <span>{results.length} results \u00b7 $0.0002</span>
          </div>
        </div>
      )}
    </div>
  );
}

function CompareView({ agentResult, agentLoading }) {
  return (
    <div style={{ animation: "fadeIn 0.4s ease" }}>
      {agentLoading && (
        <div style={{
          background: "var(--bg-secondary)", border: "1px solid var(--accent-purple)33",
          borderRadius: "var(--radius-lg)", padding: "48px", textAlign: "center", marginBottom: 32,
        }}>
          <div style={{ fontSize: 15, color: "var(--accent-purple)", animation: "pulse 1.5s infinite", fontFamily: "'JetBrains Mono', monospace", marginBottom: 8 }}>
            Agent reasoning...
          </div>
          <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>
            Decomposing query \u2192 Searching sub-queries \u2192 Cross-encoder reranking \u2192 Generating answer \u2192 Grounding check
          </div>
        </div>
      )}

      {agentResult && !agentLoading && (
        <div style={{ marginBottom: 40, animation: "fadeInUp 0.5s ease both" }}>
          <div style={{ display: "flex", gap: 24 }}>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ marginBottom: 16 }}>
                <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: 22, fontWeight: 700, marginBottom: 6, letterSpacing: "-0.02em" }}>
                  Agent Answer
                </h2>
                <div style={{ display: "flex", gap: 8, marginBottom: 4 }}>
                  <Pill color="var(--accent-purple)">{agentResult.query_type || "agent"}</Pill>
                  {agentResult.retries > 0 && <Pill color="var(--accent-amber)">Self-corrected</Pill>}
                  <Pill color="var(--accent-cyan)">{(agentResult.latency_ms / 1000).toFixed(1)}s</Pill>
                </div>
              </div>
              <div style={{
                background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-lg)", padding: "24px", marginBottom: 16,
              }}>
                <div className="agent-markdown" style={{ fontSize: 14, lineHeight: 1.8, color: "var(--text-primary)" }}>
                  <style>{`
                    .agent-markdown table { width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 13px; background: var(--bg-secondary); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); overflow: hidden; }
                    .agent-markdown th { background: var(--bg-tertiary); color: var(--text-primary); font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 14px; padding: 16px 20px; text-align: center; border-bottom: 1px solid var(--border-subtle); }
                    .agent-markdown th:first-child { text-align: center; }
                    .agent-markdown th:nth-child(2) { background: rgba(0, 212, 170, 0.06); }
                    .agent-markdown td { padding: 14px 20px; text-align: center; border-bottom: 1px solid var(--border-subtle); color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; font-size: 12px; }
                    .agent-markdown td:first-child { text-align: center; font-weight: 700; }
                    .agent-markdown td:nth-child(2) { background: rgba(0, 212, 170, 0.06); }
                    .agent-markdown tr:hover { background: var(--bg-tertiary); }
                    .agent-markdown tr:hover td:nth-child(2) { background: rgba(0, 212, 170, 0.1); }
                    .agent-markdown h2 { font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 700; margin: 28px 0 14px; letter-spacing: -0.02em; color: var(--text-primary); }
                    .agent-markdown h3 { font-family: 'Outfit', sans-serif; font-size: 16px; font-weight: 600; margin: 22px 0 10px; color: var(--text-primary); }
                    .agent-markdown strong { color: var(--text-primary); font-weight: 700; }
                    .agent-markdown hr { border: none; border-top: 1px solid var(--border-subtle); margin: 24px 0; }
                    .agent-markdown ul, .agent-markdown ol { padding-left: 20px; margin: 10px 0; }
                    .agent-markdown li { margin: 6px 0; color: var(--text-secondary); line-height: 1.6; }
                    .agent-markdown li strong { color: var(--accent-cyan); }
                    .agent-markdown p { margin: 10px 0; line-height: 1.7; }
                    .agent-markdown p:last-child strong:first-child { color: var(--accent-cyan); }
                    .agent-markdown a { color: var(--accent-blue); text-decoration: none; }
                  `}</style>
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{agentResult.answer}</ReactMarkdown>
                </div>
              </div>
              <div style={{
                background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
                borderRadius: "var(--radius-lg)", padding: "20px",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <span style={{ fontSize: 13, fontWeight: 600 }}>Grounding Verification</span>
                  <span style={{
                    fontSize: 22, fontWeight: 700, fontFamily: "'Outfit', sans-serif",
                    color: agentResult.grounding.score > 0.7 ? "var(--accent-green)" : agentResult.grounding.score > 0.4 ? "var(--accent-amber)" : "var(--accent-red)",
                  }}>{(agentResult.grounding.score * 100).toFixed(0)}%</span>
                </div>
                <div style={{ height: 8, background: "var(--bg-tertiary)", borderRadius: 4, overflow: "hidden", marginBottom: 12 }}>
                  <div style={{
                    height: "100%", borderRadius: 4, transition: "width 0.5s",
                    width: (agentResult.grounding.score * 100) + "%",
                    background: agentResult.grounding.score > 0.7 ? "var(--accent-green)" : agentResult.grounding.score > 0.4 ? "var(--accent-amber)" : "var(--accent-red)",
                  }} />
                </div>
                <div style={{ fontSize: 11, color: "var(--text-secondary)", fontFamily: "'JetBrains Mono', monospace", marginBottom: 12 }}>
                  {agentResult.grounding.supported}/{agentResult.grounding.total} claims verified against source documents
                </div>
                {agentResult.grounding.claims && agentResult.grounding.claims.map((c, i) => (
                  <div key={i} style={{
                    display: "flex", gap: 8, alignItems: "flex-start", fontSize: 12,
                    padding: "8px 12px", borderRadius: "var(--radius-sm)", marginBottom: 4,
                    background: c.status === "SUPPORTED" ? "var(--accent-green-dim)" : c.status === "UNSUPPORTED" ? "var(--accent-red-dim)" : "var(--accent-amber-dim)",
                    animation: "fadeIn 0.3s ease " + (i * 0.05) + "s both",
                  }}>
                    {c.status === "SUPPORTED" ? <CheckIcon /> : c.status === "UNSUPPORTED" ? <XIcon /> : <AlertIcon />}
                    <span style={{ color: "var(--text-secondary)", lineHeight: 1.5 }}>{c.claim}</span>
                  </div>
                ))}
              </div>
            </div>
            <div style={{
              width: 300, flexShrink: 0, background: "var(--bg-secondary)",
              border: "1px solid var(--border-subtle)", borderRadius: "var(--radius-lg)",
              padding: "20px", alignSelf: "flex-start", position: "sticky", top: 84,
            }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <h3 style={{ fontSize: 13, fontWeight: 700, fontFamily: "'Outfit', sans-serif", display: "flex", alignItems: "center", gap: 8 }}>
                  <ActivityIcon /> Agent Trace
                </h3>
                <Pill color="var(--accent-purple)">Live</Pill>
              </div>
              {agentResult.trace && agentResult.trace.map((step, i) => (
                <div key={i} style={{ display: "flex", gap: 12, marginBottom: 14, animation: "fadeInUp 0.4s ease " + (i * 0.12) + "s both" }}>
                  <div style={{
                    width: 26, height: 26, borderRadius: "50%", flexShrink: 0,
                    background: "var(--accent-purple-dim)", border: "2px solid var(--accent-purple)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}><CheckIcon /></div>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>{step.step}</div>
                    <div style={{ fontSize: 11, color: "var(--text-secondary)", fontFamily: "'JetBrains Mono', monospace", marginTop: 2 }}>
                      {step.result && typeof step.result === "string" && step.result}
                      {step.grounding_score !== undefined && "Score: " + (step.grounding_score * 100).toFixed(0) + "%"}
                      {step.total_results !== undefined && step.total_results + " results"}
                      {step.tokens !== undefined && step.tokens + " tokens"}
                      {step.reason && step.reason}
                      {step.refined_queries && step.refined_queries.join(", ")}
                    </div>
                  </div>
                </div>
              ))}
              <div style={{
                marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--border-subtle)",
                fontSize: 11, fontFamily: "'JetBrains Mono', monospace", color: "var(--text-secondary)",
                display: "flex", justifyContent: "space-between",
              }}>
                <span>Total: {(agentResult.latency_ms / 1000).toFixed(1)}s</span>
                <span>{agentResult.retries > 0 ? "retried " + agentResult.retries + "x" : "first pass"}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {!agentResult && !agentLoading && (
        <div style={{ marginBottom: 24 }}>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: 22, fontWeight: 700, marginBottom: 6, letterSpacing: "-0.02em" }}>
            API Comparison
          </h2>
          <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
            "Compare payment APIs with recurring billing, sandbox, and under 3% fees"
          </p>
          <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 6, fontFamily: "'JetBrains Mono', monospace" }}>
            <span style={{ color: "var(--accent-purple)" }}>Multi-step agent</span> {"\u00b7"} 3 sub-queries {"\u00b7"} 4 APIs compared {"\u00b7"} 2.4s
          </div>
        </div>
      )}
      {!agentResult && !agentLoading && <ComparisonTable />}
    </div>
  );
}

function ObservabilityView() {
  const chartData1 = [85, 86.5, 87, 86.8, 88, 87.5, 88.5, 89, 89.2];
  const chartData2 = [5.1, 4.8, 4.2, 4.0, 3.8, 3.5, 3.4, 3.3, 3.2];
  const chartData3 = [2.1, 2.0, 1.95, 2.05, 1.9, 1.88, 1.85, 1.83, 1.82];

  return (
    <div style={{ animation: "fadeIn 0.4s ease" }}>
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: 22, fontWeight: 700, marginBottom: 6, letterSpacing: "-0.02em" }}>
          System Observability
        </h2>
        <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
          Live metrics from production · Last updated 12s ago
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14, marginBottom: 28 }}>
        {METRICS.map((m, i) => <MetricCard key={m.label} {...m} delay={i * 0.08} />)}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 28 }}>
        <div style={{
          background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-lg)", padding: "22px 24px",
          animation: "fadeInUp 0.5s ease 0.3s both",
        }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <LayersIcon /> Precision@5 Trend
          </h3>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 16 }}>
            <MiniChart data={chartData1} color="var(--accent-cyan)" height={60} width={200} />
            <div style={{ fontSize: 11, color: "var(--text-secondary)", fontFamily: "'JetBrains Mono', monospace" }}>
              <div>Peak: 89.2%</div>
              <div style={{ color: "var(--accent-green)", marginTop: 2 }}>↑ Steady climb</div>
            </div>
          </div>
        </div>
        <div style={{
          background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-lg)", padding: "22px 24px",
          animation: "fadeInUp 0.5s ease 0.4s both",
        }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <AlertIcon /> Hallucination Rate
          </h3>
          <div style={{ display: "flex", alignItems: "flex-end", gap: 16 }}>
            <MiniChart data={chartData2} color="var(--accent-amber)" height={60} width={200} />
            <div style={{ fontSize: 11, color: "var(--text-secondary)", fontFamily: "'JetBrains Mono', monospace" }}>
              <div>Current: 3.2%</div>
              <div style={{ color: "var(--accent-green)", marginTop: 2 }}>↓ Improving</div>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <div style={{
          background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-lg)", padding: "22px 24px",
          animation: "fadeInUp 0.5s ease 0.5s both",
        }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <BoxIcon /> Multi-Cloud Routing
          </h3>
          <CloudRoutingPanel />
        </div>
        <div style={{
          background: "var(--bg-secondary)", border: "1px solid var(--border-subtle)",
          borderRadius: "var(--radius-lg)", padding: "22px 24px",
          animation: "fadeInUp 0.5s ease 0.6s both",
        }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <GitIcon /> Recent Evaluations
          </h3>
          {[
            { commit: "a3f82d1", msg: "Adaptive chunking v2", pAtK: "89.2%", status: "pass" },
            { commit: "7e1bc44", msg: "Add cross-encoder rerank", pAtK: "87.1%", status: "pass" },
            { commit: "d9f3a02", msg: "Tune grounding threshold", pAtK: "86.5%", status: "pass" },
            { commit: "1b4e7f9", msg: "Naive chunking baseline", pAtK: "62.3%", status: "baseline" },
          ].map((ev, i) => (
            <div key={ev.commit} style={{
              display: "flex", alignItems: "center", gap: 12,
              padding: "10px 12px", borderRadius: "var(--radius-sm)",
              background: i === 0 ? "var(--accent-cyan-dim)" : "transparent",
              marginBottom: 4, animation: `fadeIn 0.3s ease ${0.7 + i * 0.08}s both`,
            }}>
              <span style={{
                fontFamily: "'JetBrains Mono', monospace", fontSize: 11,
                color: "var(--accent-purple)", minWidth: 60,
              }}>{ev.commit}</span>
              <span style={{ flex: 1, fontSize: 12, color: "var(--text-secondary)" }}>{ev.msg}</span>
              <span style={{
                fontFamily: "'JetBrains Mono', monospace", fontSize: 11, fontWeight: 600,
                color: ev.status === "baseline" ? "var(--text-secondary)" : "var(--accent-cyan)",
              }}>{ev.pAtK}</span>
              <Pill color={ev.status === "pass" ? "var(--accent-green)" : "var(--text-secondary)"}>{ev.status}</Pill>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── MAIN APP ───────────────────────────────────

export default function APIUniverse() {
  const [view, setView] = useState("search");
  const [query, setQuery] = useState("");
  const [token, setToken] = useState("");
  const [liveResults, setLiveResults] = useState(null);
  const [liveLatency, setLiveLatency] = useState(null);
  const [loading, setLoading] = useState(false);
  const [agentResult, setAgentResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    axios.post(API_URL + "/token", { user_id: "demo-user" })
      .then(res => setToken(res.data.access_token))
      .catch(() => setError("Cannot connect to backend API"));
  }, []);

  const tabs = [
    { id: "search", label: "Search", icon: <SearchIcon /> },
    { id: "results", label: "Results", icon: <LayersIcon /> },
    { id: "compare", label: "Compare", icon: <BoxIcon /> },
    { id: "observability", label: "Observability", icon: <ActivityIcon /> },
  ];

  const handleSearch = async (q) => {
    if (!q || !q.trim() || !token) return;
    setQuery(q);
    setLoading(true);
    setError("");
    try {
      const res = await axios.post(API_URL + "/search", { query: q, top_k: 5 }, {
        headers: { Authorization: "Bearer " + token }
      });
      const transformed = res.data.results.map(r => ({
        name: r.metadata.api_name || "Unknown API",
        category: r.metadata.type || "API",
        score: r.rerank_score !== undefined ? Math.max(0, Math.min(1, (r.rerank_score + 12) / 16)) : r.score,
        auth: r.metadata.method ? r.metadata.method + " " + (r.metadata.path || "") : "REST",
        pricing: r.rerank_score !== undefined ? "rerank: " + r.rerank_score.toFixed(2) : "sim: " + r.score.toFixed(3),
        description: r.text.substring(0, 300) + (r.text.length > 300 ? "..." : ""),
        endpoints: r.metadata.path ? [r.metadata.method + " " + r.metadata.path] : [],
        tags: r.metadata.tags || [],
        citations: 0,
      }));
      setLiveResults(transformed);
      setLiveLatency(res.data.latency_ms);
      setView("results");
    } catch (e) {
      setError(e.response?.data?.detail || "Search failed. Is the backend running?");
    }
    setLoading(false);
  };

  const handleAgent = async (q) => {
    if (!q || !q.trim() || !token) return;
    setQuery(q);
    setLoading(true);
    setError("");
    try {
      const res = await axios.post(API_URL + "/agent", { query: q }, {
        headers: { Authorization: "Bearer " + token }
      });
      setAgentResult(res.data);
      setView("compare");
    } catch (e) {
      setError(e.response?.data?.detail || "Agent failed. Is the backend running?");
    }
    setLoading(false);
  };

  const handleCompare = async () => {
    if (!liveResults || !liveResults.length || !token) return;
    const apiNames = [...new Set(liveResults.map(r => r.name))].slice(0, 5);
    const compareQuery = "Compare " + apiNames.join(", ") + " for: " + query;
    setLoading(true);
    setError("");
    try {
      const res = await axios.post(API_URL + "/agent", { query: compareQuery }, {
        headers: { Authorization: "Bearer " + token }
      });
      setAgentResult(res.data);
      setView("compare");
    } catch (e) {
      setError(e.response?.data?.detail || "Agent failed. Is the backend running?");
    }
    setLoading(false);
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg-primary)", color: "var(--text-primary)" }}>
      <style>{FONTS_CSS}</style>

      {/* NAV */}
      <nav style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 32px", height: 64,
        borderBottom: "1px solid var(--border-subtle)",
        background: "var(--bg-primary)",
        position: "sticky", top: 0, zIndex: 100,
        backdropFilter: "blur(12px)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
          <div
            onClick={() => setView("search")}
            style={{
              fontFamily: "'Outfit', sans-serif", fontSize: 18, fontWeight: 800,
              letterSpacing: "-0.03em", cursor: "pointer",
              background: "linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))",
              WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent",
            }}>
            ◆ API Universe
          </div>
          <div style={{ display: "flex", gap: 2 }}>
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setView(tab.id)}
                style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "8px 14px", borderRadius: "var(--radius-sm)",
                  background: view === tab.id ? "var(--bg-elevated)" : "transparent",
                  border: "none", color: view === tab.id ? "var(--text-primary)" : "var(--text-secondary)",
                  fontSize: 13, fontWeight: 500, cursor: "pointer",
                  transition: "all 0.15s ease",
                  fontFamily: "'DM Sans', sans-serif",
                }}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <Pill color="var(--accent-green)" filled>2,529 APIs indexed</Pill>
          <div style={{
            width: 32, height: 32, borderRadius: "50%",
            background: "linear-gradient(135deg, var(--accent-blue), var(--accent-purple))",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 13, fontWeight: 700, color: "#fff", fontFamily: "'Outfit', sans-serif",
          }}>Y</div>
        </div>
      </nav>

      {error && <div style={{ padding: "10px 32px", background: "var(--accent-red-dim)", color: "var(--accent-red)", fontSize: 13 }}>{error}</div>}
      {loading && <div style={{ padding: "10px 32px", background: "var(--accent-blue-dim)", color: "var(--accent-blue)", fontSize: 13, animation: "pulse 1.5s infinite" }}>Searching 125,655 vectors...</div>}

      {/* CONTENT */}
      <main style={{ maxWidth: 1200, margin: "0 auto", padding: view === "search" ? "0" : "32px 32px 60px" }}>
        {view === "search" && <SearchView onSearch={handleSearch} onAgent={handleAgent} view="search" />}
        {view === "results" && <ResultsView query={query} onBack={() => setView("search")} liveResults={liveResults} liveLatency={liveLatency} onSearch={handleSearch} onCompare={handleCompare} comparing={loading} />}
        {view === "compare" && <CompareView agentResult={agentResult} agentLoading={loading} />}
        {view === "observability" && <ObservabilityView />}
      </main>
    </div>
  );
}

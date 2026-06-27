import { useState, useEffect, useRef, useCallback } from "react";
import {
  Brain,
  Check,
  ChevronDown,
  ChevronRight,
  Clock,
  Edit3,
  Loader2,
  Minus,
  Sparkles,
  X,
  Zap,
} from "lucide-react";

// ─── API ──────────────────────────────────────────────────────────────────
const API = "http://localhost:8000";

const ACCOUNTS: Record<string, { name: string; label: string }> = {
  acme_corp: { name: "Acme Corp", label: "Acme Corp — At Risk" },
  techcorp: { name: "TechCorp", label: "TechCorp — Onboarding" },
  globex_corp: { name: "Globex Corp", label: "Globex Corp — Healthy" },
  nexus_systems: { name: "Nexus Systems", label: "Nexus Systems — At Risk" },
  bluewave_tech: { name: "BlueWave Tech", label: "BlueWave Tech — At Risk" },
};

// ─── Types ─────────────────────────────────────────────────────────────────
interface AgentStep {
  agent_name: string;
  action: string;
  reasoning: string;
  duration_ms: number;
}

interface Evidence {
  id: string;
  source_type: string;
  source_name: string;
  excerpt: string;
  relevance_score: number;
}

interface Action {
  title: string;
  description: string;
  confidence: number;
  estimated_impact: string;
  evidence_ids: string[];
  precedent_accounts: string[];
}

interface MemoryContext {
  similar_cases_found: number;
  confidence_boost: number;
  base_confidence: number;
  boosted_confidence: number;
  precedent_accounts: string[];
}

interface AnalysisResult {
  request_id: string;
  account_name: string;
  csm_name: string;
  renewal_date: string;
  risk_score: number;
  risk_level: string;
  signal_count: number;
  agent_trace: AgentStep[];
  evidence: Evidence[];
  primary_recommendation: Action;
  alternatives: Action[];
  memory_context: MemoryContext | null;
}

// ─── Design tokens ──────────────────────────────────────────────────────────
const C = {
  bg: "#08090D",
  surface: "#10131A",
  sidebar: "#0C0E14",
  indigo: "#6366F1",
  indigoLight: "#818CF8",
  indigoPurple: "#A78BFA",
  success: "#10B981",
  danger: "#EF4444",
  warning: "#F59E0B",
  amber: "#FB923C",
  textPrimary: "#F1F5F9",
  textSecondary: "#94A3B8",
  textMuted: "#4B5563",
  border: "rgba(255,255,255,0.07)",
  borderHover: "rgba(255,255,255,0.14)",
};

const RISK_COLORS: Record<string, string> = {
  critical: C.danger,
  high: C.warning,
  medium: C.amber,
  low: C.success,
};

// ─── Donut gauge ────────────────────────────────────────���───────────────────
function DonutGauge({ pct, level }: { pct: number; level: string }) {
  const r = 50;
  const cx = 60;
  const cy = 60;
  const sw = 10;
  const circ = 2 * Math.PI * r;
  const [drawn, setDrawn] = useState(0);

  useEffect(() => {
    const t = setTimeout(() => setDrawn(pct), 100);
    return () => clearTimeout(t);
  }, [pct]);

  const offset = circ - (drawn / 100) * circ;
  const color = RISK_COLORS[level] || C.danger;

  return (
    <svg width={120} height={120} viewBox="0 0 120 120">
      <defs>
        <linearGradient id="arcGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={color} />
          <stop offset="100%" stopColor={C.danger} />
        </linearGradient>
      </defs>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth={sw} />
      <circle
        cx={cx} cy={cy} r={r} fill="none"
        stroke="url(#arcGrad)" strokeWidth={sw}
        strokeDasharray={circ} strokeDashoffset={offset}
        strokeLinecap="round" transform={`rotate(-90 ${cx} ${cy})`}
        style={{ transition: "stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)" }}
      />
      <text x={cx} y={cy - 6} textAnchor="middle" fill={C.textPrimary} fontSize={22} fontWeight={600} fontFamily="Inter,sans-serif">
        {pct}%
      </text>
      <text x={cx} y={cy + 14} textAnchor="middle" fill={C.textMuted} fontSize={10} fontFamily="Inter,sans-serif">
        Churn risk
      </text>
    </svg>
  );
}

// ─── Signal pill ─────────────────────────────────────────────────────────────
function SignalPill({ label, color, text }: { label: string; color: string; text: string }) {
  return (
    <div style={{
      background: `${color}1F`, border: `1px solid ${color}40`,
      borderRadius: 6, padding: "4px 10px", fontSize: 11, color: text,
      display: "flex", alignItems: "center", gap: 6, position: "relative", overflow: "hidden",
    }}>
      <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: 4, background: text, borderRadius: "6px 0 0 6px" }} />
      <span style={{ marginLeft: 6 }}>{label}</span>
    </div>
  );
}

// ─── Evidence card ───────────────────────────────────────────────────────────
function EvidenceCard({ badge, badgeColor, text, relevance, barColor }: {
  badge: string; badgeColor: string; text: string; relevance: number; barColor: string;
}) {
  const [width, setWidth] = useState(0);
  useEffect(() => { const t = setTimeout(() => setWidth(relevance), 300); return () => clearTimeout(t); }, [relevance]);

  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 10, padding: 12, display: "flex", flexDirection: "column", gap: 8 }}>
      <span style={{ fontSize: 10, borderRadius: 4, padding: "2px 6px", background: `${badgeColor}1F`, color: badgeColor, fontWeight: 500, alignSelf: "flex-start" }}>{badge}</span>
      <p style={{ fontSize: 12, color: C.textSecondary, lineHeight: 1.5, margin: 0 }}>{text}</p>
      <div>
        <div style={{ height: 3, borderRadius: 2, background: C.border, position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${width}%`, background: barColor, borderRadius: 2, transition: "width 1s cubic-bezier(0.4,0,0.2,1)" }} />
        </div>
        <div style={{ fontSize: 10, color: C.textMuted, textAlign: "right", marginTop: 3 }}>{relevance}% match</div>
      </div>
    </div>
  );
}

// ─── Confidence bar ───────────────────────────────────────────────────────────
function ConfidenceBar({ base, boosted }: { base: number; boosted: number }) {
  const [w, setW] = useState(0);
  useEffect(() => { const t = setTimeout(() => setW(boosted), 400); return () => clearTimeout(t); }, [boosted]);
  const boostPct = w - base;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11 }}>
        <span style={{ color: C.textMuted }}>Base {base}%</span>
        <span style={{ color: C.success, fontWeight: 500 }}>{boosted}% boosted</span>
      </div>
      <div style={{ height: 6, borderRadius: 3, background: C.border, position: "relative", overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${base}%`, background: C.textMuted, borderRadius: 3 }} />
        <div style={{ position: "absolute", left: `${base}%`, top: 0, bottom: 0, width: `${boostPct}%`, background: C.indigo, borderRadius: 3, transition: "width 1s cubic-bezier(0.4,0,0.2,1)" }} />
      </div>
      <div style={{ fontSize: 11, color: C.success }}>+{boostPct}% confidence from memory</div>
    </div>
  );
}

// ─── Agent trace step ─────────────────────────────────────────────────────────
function AgentStep({ label, color, time, action, isLast }: {
  label: string; color: string; time: string; action: string; isLast: boolean;
}) {
  return (
    <div style={{ display: "flex", gap: 10, position: "relative" }}>
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 0 }}>
        <div style={{ width: 6, height: 6, borderRadius: "50%", background: color, marginTop: 4, flexShrink: 0 }} />
        {!isLast && <div style={{ width: 1, flex: 1, background: C.border, marginTop: 4 }} />}
      </div>
      <div style={{ flex: 1, paddingBottom: isLast ? 0 : 14, minWidth: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
          <span style={{ fontSize: 10, fontWeight: 500, padding: "1px 6px", borderRadius: 4, background: `${color}33`, color, flexShrink: 0 }}>{label}</span>
          <span style={{ fontSize: 11, color: C.textMuted, fontFamily: "monospace", flexShrink: 0 }}>{time}</span>
        </div>
        <p style={{ fontSize: 12, color: C.textSecondary, margin: "4px 0 0", lineHeight: 1.4 }}>{action}</p>
      </div>
    </div>
  );
}

// ─── Source type helpers ──────────────────────────────────────────────────────
const SOURCE_COLORS: Record<string, string> = {
  meeting_note: "#818CF8",
  playbook: "#A78BFA",
  memory: "#10B981",
  crm: "#FB923C",
};

const SOURCE_LABELS: Record<string, string> = {
  meeting_note: "Meeting note",
  playbook: "Playbook",
  memory: "Memory",
  crm: "CRM profile",
};

// ─── Main app ─────────────────────────────────────────────────────────────────
export default function App() {
  const [accountId, setAccountId] = useState("acme_corp");
  const [transcript, setTranscript] = useState("");
  const [analysing, setAnalysing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [decision, setDecision] = useState<"none" | "accepted" | "modifying" | "rejecting">("none");
  const [modifyText, setModifyText] = useState("");
  const [modifySubmitted, setModifySubmitted] = useState(false);
  const [evidenceOpen, setEvidenceOpen] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Check backend health on mount
  useEffect(() => {
    fetch(`${API}/health`)
      .then(r => r.json())
      .then(d => setBackendOk(d.status === "ok"))
      .catch(() => setBackendOk(false));
  }, []);

  const handleAnalyse = useCallback(async () => {
    if (!transcript.trim()) return;
    setAnalysing(true);
    setError(null);
    setResult(null);
    setDecision("none");
    setModifySubmitted(false);

    try {
      const resp = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_id: accountId, interaction_text: transcript }),
      });
      if (!resp.ok) {
        const text = await resp.text();
        throw new Error(`API error ${resp.status}: ${text}`);
      }
      const data: AnalysisResult = await resp.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Analysis failed");
    } finally {
      setAnalysing(false);
    }
  }, [accountId, transcript]);

  const handleAccept = useCallback(async () => {
    if (!result) return;
    try {
      await fetch(`${API}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: result.request_id, decision: "accepted", modification_notes: "" }),
      });
    } catch (_) {}
    setDecision("accepted");
  }, [result]);

  const handleReject = useCallback(async () => {
    if (!result) return;
    try {
      await fetch(`${API}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: result.request_id, decision: "rejected", modification_notes: "" }),
      });
    } catch (_) {}
    setDecision("rejecting");
  }, [result]);

  const handleModifySubmit = useCallback(async () => {
    if (!result) return;
    try {
      await fetch(`${API}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ request_id: result.request_id, decision: "modified", modification_notes: modifyText }),
      });
    } catch (_) {}
    setModifySubmitted(true);
  }, [result, modifyText]);

  // Format duration
  const fmtDuration = (ms: number) => {
    if (ms < 1000) return `${ms} ms`;
    return `${(ms / 1000).toFixed(1)} s`;
  };

  const totalMs = result?.agent_trace?.reduce((a, s) => a + s.duration_ms, 0) || 0;
  const pct = result ? Math.round(result.risk_score * 100) : 0;
  const riskColor = result ? RISK_COLORS[result.risk_level] || C.danger : C.textMuted;

  const AGENT_LABELS: Record<string, string> = {
    planner: "PLANNER",
    interaction_analyzer: "INTERACTION",
    knowledge_retriever: "KNOWLEDGE",
    risk_assessor: "RISK",
    nba_generator: "NBA",
  };

  const AGENT_COLORS: Record<string, string> = {
    planner: "#818CF8",
    interaction_analyzer: "#818CF8",
    knowledge_retriever: "#A78BFA",
    risk_assessor: "#F59E0B",
    nba_generator: "#10B981",
  };

  return (
    <div style={{
      display: "flex", height: "100vh", width: "100%",
      background: C.bg, fontFamily: "Inter, sans-serif",
      color: C.textPrimary, overflow: "hidden", minWidth: 1280,
    }}>
      {/* ── LEFT SIDEBAR ─────────────────────────────────────────────────── */}
      <aside style={{
        width: 256, flexShrink: 0, background: C.sidebar,
        borderRight: `1px solid ${C.border}`,
        display: "flex", flexDirection: "column", height: "100vh", overflow: "hidden",
      }}>
        {/* Branding */}
        <div style={{ padding: "16px 16px 12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.indigo }} />
            <span style={{ fontSize: 17, fontWeight: 600, color: C.textPrimary }}>Meridian</span>
          </div>
          <div style={{ fontSize: 11, color: C.textMuted, marginTop: 2, paddingLeft: 16 }}>Decision intelligence</div>
        </div>
        <div style={{ height: 1, background: C.border }} />

        <div style={{ padding: "12px 16px", flex: 1, overflow: "auto", display: "flex", flexDirection: "column", gap: 14 }}>
          {/* Account */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 500, color: C.textMuted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>Account</div>
            <div style={{ position: "relative" }}>
              <select
                value={accountId}
                onChange={e => { setAccountId(e.target.value); setResult(null); setDecision("none"); }}
                style={{
                  width: "100%", background: C.bg, border: `1px solid ${C.border}`,
                  borderRadius: 8, padding: "7px 28px 7px 10px", fontSize: 12,
                  color: C.textPrimary, appearance: "none", cursor: "pointer", outline: "none",
                }}
              >
                {Object.entries(ACCOUNTS).map(([id, acct]) => (
                  <option key={id} value={id}>{acct.label}</option>
                ))}
              </select>
              <ChevronDown size={12} style={{ position: "absolute", right: 8, top: "50%", transform: "translateY(-50%)", color: C.textMuted, pointerEvents: "none" }} />
            </div>
          </div>

          {/* Transcript */}
          <div>
            <div style={{ fontSize: 10, fontWeight: 500, color: C.textMuted, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>Meeting Transcript</div>
            <textarea
              ref={textareaRef}
              value={transcript}
              onChange={e => setTranscript(e.target.value)}
              placeholder="Paste meeting notes, call transcript, or CRM update…"
              style={{
                width: "100%", minHeight: 160,
                background: C.bg, border: `1px solid rgba(255,255,255,0.1)`,
                borderRadius: 8, padding: "8px 10px", fontSize: 12, color: C.textPrimary,
                resize: "vertical", outline: "none", boxSizing: "border-box",
                lineHeight: 1.5, fontFamily: "Inter, sans-serif",
              }}
            />
          </div>

          {/* Analyse button */}
          <button
            onClick={handleAnalyse}
            disabled={analysing || !transcript.trim()}
            style={{
              width: "100%", height: 36, background: C.indigo, color: "#fff",
              border: "none", borderRadius: 8, fontSize: 13, fontWeight: 500,
              cursor: analysing ? "default" : "pointer",
              display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              opacity: analysing ? 0.8 : 1,
            }}
          >
            {analysing ? (
              <><Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} /> Analysing…</>
            ) : (
              <><Zap size={14} /> Analyse account</>
            )}
          </button>
        </div>

        {/* Bottom status */}
        <div style={{ padding: "10px 16px", borderTop: `1px solid ${C.border}`, display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{
            width: 6, height: 6, borderRadius: "50%",
            background: backendOk === null ? C.textMuted : backendOk ? C.success : C.danger,
            boxShadow: backendOk ? `0 0 6px ${C.success}` : "none",
            animation: backendOk ? "pulse 2s ease-in-out infinite" : "none",
          }} />
          <span style={{ fontSize: 11, color: C.textSecondary }}>
            {backendOk === null ? "Checking…" : backendOk ? "Backend connected" : "Backend offline"}
          </span>
        </div>
      </aside>

      {/* ── MAIN CONTENT ─────────────────────────────────────────────────── */}
      <main style={{ flex: 1, overflow: "auto", padding: "16px 20px", display: "flex", flexDirection: "column", gap: 14 }}>

        {!result && !analysing && !error && (
          <div style={{
            flex: 1, display: "flex", flexDirection: "column", alignItems: "center",
            justifyContent: "center", textAlign: "center", color: C.textMuted, gap: 12,
          }}>
            <div style={{ fontSize: 40, marginBottom: 8 }}>🧭</div>
            <div style={{ fontSize: 18, fontWeight: 600, color: C.textSecondary }}>Select an account and paste a transcript</div>
            <div style={{ fontSize: 13, maxWidth: 400, lineHeight: 1.6 }}>
              The 5-agent pipeline will extract signals, retrieve knowledge from ChromaDB, assess risk, and generate next-best-action recommendations.
            </div>
          </div>
        )}

        {analysing && (
          <div style={{
            flex: 1, display: "flex", flexDirection: "column", alignItems: "center",
            justifyContent: "center", gap: 12,
          }}>
            <Loader2 size={32} style={{ animation: "spin 1s linear infinite", color: C.indigo }} />
            <div style={{ fontSize: 14, color: C.textSecondary }}>Running agent pipeline…</div>
            <div style={{ fontSize: 11, color: C.textMuted }}>Planner → Analyzer → Knowledge → Risk → NBA</div>
          </div>
        )}

        {error && (
          <div style={{
            background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
            borderRadius: 8, padding: "14px 16px", color: C.danger, fontSize: 13,
          }}>
            {error}
          </div>
        )}

        {result && (
          <>
            {/* Account header bar */}
            <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "nowrap" }}>
              <div style={{
                width: 32, height: 32, borderRadius: "50%",
                background: "#1E1F3B", color: C.indigo,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 13, fontWeight: 600, flexShrink: 0,
              }}>{result.account_name.charAt(0).toUpperCase()}{result.account_name.charAt(1).toLowerCase()}</div>
              <span style={{ fontSize: 15, fontWeight: 600, color: C.textPrimary }}>{result.account_name}</span>
              <span style={{ color: C.textMuted, fontSize: 12 }}>·</span>
              <span style={{ fontSize: 12, color: C.textSecondary }}>CSM: {result.csm_name}</span>
              <span style={{ color: C.textMuted, fontSize: 12 }}>·</span>
              <span style={{ fontSize: 12, color: C.textSecondary }}>Renewal: {result.renewal_date}</span>
              <div style={{ flex: 1 }} />
              <div style={{
                padding: "4px 10px",
                background: `${riskColor}1A`,
                border: `1px solid ${riskColor}44`,
                borderRadius: 20, fontSize: 11, fontWeight: 500,
                color: riskColor, whiteSpace: "nowrap",
              }}>{result.risk_level.charAt(0).toUpperCase() + result.risk_level.slice(1)} · {pct}% churn risk</div>
            </div>

            {/* Risk and signals card */}
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderRadius: 10, padding: "16px",
              display: "grid", gridTemplateColumns: "auto 1fr", gap: 20, alignItems: "center",
            }}>
              <DonutGauge pct={pct} level={result.risk_level} />
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                <div style={{ fontSize: 12, color: C.textMuted }}>{result.signal_count} signal{result.signal_count !== 1 ? "s" : ""} detected</div>
                {result.agent_trace.find(s => s.agent_name === "interaction_analyzer")?.reasoning?.includes("Found") && (
                  <span style={{ fontSize: 10, color: C.textMuted }}>{result.agent_trace.find(s => s.agent_name === "interaction_analyzer")?.reasoning}</span>
                )}
              </div>
            </div>

            {/* Evidence section */}
            {result.evidence.length > 0 && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                  <span style={{ fontSize: 13, fontWeight: 500, color: C.textPrimary }}>Evidence</span>
                  <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 20, background: "rgba(99,102,241,0.15)", color: "#818CF8" }}>
                    {result.evidence.length} source{result.evidence.length !== 1 ? "s" : ""}
                  </span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 10 }}>
                  {result.evidence.slice(0, 3).map((ev, i) => (
                    <EvidenceCard
                      key={ev.id || i}
                      badge={SOURCE_LABELS[ev.source_type] || ev.source_type}
                      badgeColor={SOURCE_COLORS[ev.source_type] || "#818CF8"}
                      text={ev.excerpt.length > 200 ? ev.excerpt.slice(0, 200) + "…" : ev.excerpt}
                      relevance={Math.round(ev.relevance_score * 100)}
                      barColor={SOURCE_COLORS[ev.source_type] || "#818CF8"}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Memory context card */}
            {result.memory_context && result.memory_context.similar_cases_found > 0 && (
              <div style={{
                background: C.surface, border: `1px solid ${C.border}`,
                borderLeft: `3px solid ${C.indigo}`, borderRadius: 10,
                padding: "14px 16px", display: "flex", flexDirection: "column", gap: 10,
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Sparkles size={14} style={{ color: C.indigo }} />
                  <span style={{ fontSize: 13, fontWeight: 500, color: C.textPrimary }}>Memory context</span>
                  <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 20, background: "rgba(99,102,241,0.15)", color: "#818CF8" }}>
                    {result.memory_context.similar_cases_found} similar case{result.memory_context.similar_cases_found !== 1 ? "s" : ""}
                  </span>
                </div>
                <div style={{ display: "flex", gap: 6 }}>
                  {result.memory_context.precedent_accounts.map(name => (
                    <div key={name} style={{
                      display: "flex", alignItems: "center", gap: 5, fontSize: 11,
                      padding: "3px 10px", borderRadius: 20,
                      background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", color: C.success,
                    }}>
                      <Check size={10} /> {name}
                    </div>
                  ))}
                </div>
                <ConfidenceBar
                  base={Math.round(result.memory_context.base_confidence * 100)}
                  boosted={Math.round(result.memory_context.boosted_confidence * 100)}
                />
              </div>
            )}

            {/* Primary recommendation card */}
            <div style={{
              background: C.surface, border: `1px solid ${C.border}`,
              borderTop: `1px solid ${C.indigo}`, borderRadius: 10,
              padding: "16px", display: "flex", flexDirection: "column", gap: 10,
            }}>
              <div style={{ fontSize: 10, fontWeight: 500, color: C.indigo, textTransform: "uppercase", letterSpacing: "0.08em" }}>Recommended Action</div>
              <div style={{ fontSize: 17, fontWeight: 600, color: C.textPrimary, lineHeight: 1.3 }}>
                {result.primary_recommendation.title}
              </div>
              <p style={{ fontSize: 13, color: C.textSecondary, lineHeight: 1.6, margin: 0 }}>
                {result.primary_recommendation.description}
              </p>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 12 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: C.textMuted }}>
                  <Brain size={14} /> {Math.round(result.primary_recommendation.confidence * 100)}% confidence
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: C.textMuted }}>
                  <Zap size={14} /> {result.primary_recommendation.estimated_impact}
                </div>
                {result.primary_recommendation.precedent_accounts.length > 0 && (
                  <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: C.textMuted }}>
                    <Clock size={14} /> Precedents: {result.primary_recommendation.precedent_accounts.join(", ")}
                  </div>
                )}
              </div>
            </div>

            {/* Alternative actions */}
            {result.alternatives.length > 0 && (
              <div>
                <div style={{ fontSize: 12, fontWeight: 500, color: C.textSecondary, marginBottom: 8 }}>Alternative actions</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  {result.alternatives.map((alt, i) => (
                    <div key={i} style={{
                      background: C.surface, border: `1px solid ${C.border}`,
                      borderRadius: 10, padding: "12px",
                      display: "flex", flexDirection: "column", gap: 6,
                    }}>
                      <div style={{ fontSize: 13, fontWeight: 500, color: C.textPrimary, lineHeight: 1.4 }}>{alt.title}</div>
                      <div style={{ fontSize: 12, color: C.textMuted, lineHeight: 1.5, flex: 1 }}>{alt.description}</div>
                      <div style={{ display: "flex", justifyContent: "flex-end" }}>
                        <span style={{ fontSize: 11, fontWeight: 500, padding: "2px 8px", borderRadius: 20, background: `${C.textMuted}22`, color: C.textMuted, border: `1px solid ${C.textMuted}44` }}>
                          {Math.round(alt.confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* HITL decision */}
            <div style={{ marginTop: 2, marginBottom: 16 }}>
              <div style={{ fontSize: 13, fontWeight: 500, color: C.textPrimary, marginBottom: 10 }}>Your decision</div>

              {decision === "accepted" ? (
                <div style={{ display: "flex", alignItems: "center", gap: 8, background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 8, padding: "10px 14px", fontSize: 13, color: C.success }}>
                  <Check size={16} /> Recommendation accepted · logged to memory
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    <button onClick={handleAccept} style={{
                      height: 38, padding: "0 16px", background: C.success, color: "#fff",
                      border: "none", borderRadius: 8, fontSize: 13, fontWeight: 500,
                      cursor: "pointer", display: "flex", alignItems: "center", gap: 6,
                    }} onMouseEnter={e => (e.currentTarget.style.background = "#059669")}
                       onMouseLeave={e => (e.currentTarget.style.background = C.success)}>
                      <Check size={14} /> Accept recommendation
                    </button>
                    <button onClick={() => setDecision(d => d === "modifying" ? "none" : "modifying")} style={{
                      height: 38, padding: "0 16px", background: "transparent",
                      color: C.textSecondary, border: `1px solid rgba(255,255,255,0.12)`,
                      borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: "pointer",
                      display: "flex", alignItems: "center", gap: 6,
                    }}>
                      <Edit3 size={14} /> Modify
                    </button>
                    <button onClick={handleReject} style={{
                      height: 38, padding: "0 16px", background: "transparent",
                      color: C.textSecondary, border: `1px solid rgba(255,255,255,0.12)`,
                      borderRadius: 8, fontSize: 13, fontWeight: 500, cursor: "pointer",
                      display: "flex", alignItems: "center", gap: 6,
                    }} onMouseEnter={e => (e.currentTarget.style.borderColor = "rgba(239,68,68,0.4)")}
                       onMouseLeave={e => (e.currentTarget.style.borderColor = "rgba(255,255,255,0.12)")}>
                      <X size={14} /> Reject
                    </button>
                  </div>

                  {decision === "modifying" && (
                    <div style={{ overflow: "hidden", maxHeight: modifySubmitted ? 48 : 160, transition: "max-height 0.3s ease", display: "flex", flexDirection: "column", gap: 8 }}>
                      {modifySubmitted ? (
                        <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.success }}>
                          <Check size={14} /> Updated: feedback incorporated
                        </div>
                      ) : (
                        <>
                          <textarea value={modifyText} onChange={e => setModifyText(e.target.value)}
                            placeholder="What would you like to change? e.g. Change to 24-hour timeline, involve CTO instead of VP CS"
                            style={{ width: "100%", height: 80, background: C.bg, border: "1px solid rgba(255,255,255,0.1)", borderRadius: 8, padding: "8px 10px", fontSize: 12, color: C.textPrimary, resize: "none", outline: "none", boxSizing: "border-box", fontFamily: "Inter, sans-serif", lineHeight: 1.5 }} />
                          <div style={{ display: "flex", justifyContent: "flex-end" }}>
                            <button onClick={handleModifySubmit} style={{ height: 32, padding: "0 14px", background: C.indigo, color: "#fff", border: "none", borderRadius: 6, fontSize: 12, fontWeight: 500, cursor: "pointer" }}>
                              Submit and re-analyse
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  )}

                  {decision === "rejecting" && (
                    <div style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 8, padding: "10px 14px", fontSize: 12, color: C.textSecondary }}>
                      Recommendation rejected.
                    </div>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </main>

      {/* ── RIGHT PANEL ──────────────────────────────────────────────────── */}
      <aside style={{
        width: 288, flexShrink: 0, borderLeft: `1px solid ${C.border}`,
        display: "flex", flexDirection: "column", height: "100vh",
        overflow: "hidden", background: C.sidebar,
      }}>
        <div style={{ padding: "14px 16px", borderBottom: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: result ? C.success : C.textMuted }} />
              <span style={{ fontSize: 13, fontWeight: 500, color: C.textPrimary }}>Agent trace</span>
            </div>
            {result && <span style={{ fontSize: 11, color: C.textMuted }}>Completed in {fmtDuration(totalMs)}</span>}
          </div>
        </div>

        <div style={{ flex: 1, overflow: "auto", padding: "14px 16px", display: "flex", flexDirection: "column", gap: 0 }}>
          {!result && (
            <div style={{ fontSize: 12, color: C.textMuted, textAlign: "center", paddingTop: 40 }}>
              Run an analysis to see the agent trace
            </div>
          )}
          {result?.agent_trace?.map((step, i) => (
            <AgentStep
              key={i}
              label={AGENT_LABELS[step.agent_name] || step.agent_name.toUpperCase()}
              color={AGENT_COLORS[step.agent_name] || "#818CF8"}
              time={fmtDuration(step.duration_ms)}
              action={step.action === "retrieved_knowledge" ? step.reasoning : step.action === "extracted_signals" ? step.reasoning : step.action}
              isLast={i === result.agent_trace.length - 1}
            />
          ))}

          {/* Evidence sources collapsible */}
          {result && (
            <div style={{ marginTop: 16, borderTop: `1px solid ${C.border}`, paddingTop: 12 }}>
              <button onClick={() => setEvidenceOpen(o => !o)} style={{
                width: "100%", background: "none", border: "none",
                display: "flex", alignItems: "center", justifyContent: "space-between",
                fontSize: 12, color: C.textMuted, cursor: "pointer", padding: 0,
              }}>
                <span>Evidence sources ({result.evidence.length} item{result.evidence.length !== 1 ? "s" : ""})</span>
                {evidenceOpen ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
              </button>
              {evidenceOpen && (
                <div style={{ marginTop: 8, display: "flex", flexDirection: "column", gap: 4 }}>
                  {result.evidence.map((ev, i) => (
                    <div key={i} style={{ fontSize: 11, color: C.textMuted, paddingLeft: 8 }}>
                      · {SOURCE_LABELS[ev.source_type] || ev.source_type} — {ev.source_name}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </aside>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }
      `}</style>
    </div>
  );
}

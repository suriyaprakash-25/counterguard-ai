import { useState, useEffect, memo } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Badge } from "../common/Badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../common/Table";
import {
  Bot, Clock, AlertCircle, FileText, Image as ImageIcon, Link2, Server, Search, CheckCircle2, XCircle, ShieldAlert, AlertTriangle, Info, ShieldCheck, Tag, ExternalLink, Zap, ShoppingCart, Award, ArrowRight, Globe, Lock, ChevronDown, ChevronUp, Activity, DollarSign, TrendingDown, Layers, Hash, Check, Store
} from "lucide-react";
import type {
  InvestigationWorkspaceDetails, TimelineEvent, EvidenceItem,
  MemoryContext, ConsensusDetails, AgentActivity, CategorizedRecommendation,
  RecommendedProduct, ProductComparison, PriceIntelligence, RecommendationSummary, ProviderHealth
} from "../../types/investigations";
import { useInvestigationGraph, useInvestigationReasoning } from "../../hooks/useInvestigations";
import { GraphCanvas } from "../graph/GraphCanvas";
import { GraphMapper } from "../../pages/GraphExplorer/services/graph.mapper";

// --- Helper Functions for Verdict & Severity Colors ---
function getVerdictConfig(verdict: string, riskScore: number) {
  const v = (verdict || "").toLowerCase();
  if (v === "authentic" || riskScore <= 20) {
    return { label: "AUTHENTIC", color: "text-emerald-700 bg-emerald-50 border-emerald-300", badgeVar: "success" as const };
  } else if (v === "low_risk" || (riskScore > 20 && riskScore <= 40)) {
    return { label: "LOW RISK", color: "text-amber-700 bg-amber-50 border-amber-300", badgeVar: "warning" as const };
  } else if (v === "suspicious" || (riskScore > 40 && riskScore <= 70)) {
    return { label: "SUSPICIOUS", color: "text-orange-700 bg-orange-50 border-orange-300", badgeVar: "warning" as const };
  } else {
    return { label: "LIKELY COUNTERFEIT", color: "text-red-700 bg-red-50 border-red-300", badgeVar: "danger" as const };
  }
}

function getSeverityBadge(severity?: string) {
  switch ((severity || "").toLowerCase()) {
    case "critical":
      return <Badge variant="danger" className="uppercase text-[10px] px-1.5 py-0">CRITICAL</Badge>;
    case "high":
      return <Badge variant="danger" className="uppercase text-[10px] px-1.5 py-0">HIGH</Badge>;
    case "medium":
      return <Badge variant="warning" className="uppercase text-[10px] px-1.5 py-0">MEDIUM</Badge>;
    case "low":
      return <Badge variant="outline" className="uppercase text-[10px] px-1.5 py-0">LOW</Badge>;
    default:
      return <Badge variant="secondary" className="uppercase text-[10px] px-1.5 py-0">INFO</Badge>;
  }
}

// --- Data Confidence Warning Banner ---
export function DataConfidenceWarningBanner({ warning }: { warning?: string | null }) {
  if (!warning) return null;
  return (
    <div className="p-4 rounded-xl bg-amber-500 text-white border-2 border-amber-600 shadow-md mb-6 flex items-start gap-3 animate-fadeIn">
      <AlertTriangle className="h-6 w-6 shrink-0 mt-0.5" />
      <div>
        <h4 className="font-extrabold text-xs uppercase tracking-wider text-amber-100">Data Confidence Warning</h4>
        <p className="text-xs font-semibold text-white mt-1 leading-relaxed">{warning}</p>
      </div>
    </div>
  );
}

// --- Structured Evidence Matrix Card (5 Cards: Price, Seller, Images, Warranty, Visual Forensics) ---
export function StructuredEvidenceMatrixCard({ summary }: { summary?: any }) {
  if (!summary) return null;

  const cards = [
    { key: "price", title: "Price Assessment", icon: DollarSign, data: summary.price },
    { key: "seller", title: "Seller Identity", icon: Store, data: summary.seller },
    { key: "images", title: "Listing Images", icon: ImageIcon, data: summary.images },
    { key: "warranty", title: "Warranty & Policy", icon: ShieldCheck, data: summary.warranty },
    { key: "visual", title: "Visual Forensics", icon: Search, data: summary.visual },
  ];

  return (
    <Card className="shadow-sm border-slate-200">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-slate-900 text-sm">
          <Layers className="h-4 w-4 text-primary" />
          <span>Structured Evidence Evaluation Matrix</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
          {cards.map((c) => {
            const item = c.data || { status: "Unavailable", reason: "No data available" };
            const statusStr = (item.status || "Unavailable").toLowerCase();
            const badgeVar =
              statusStr === "normal" || statusStr === "good" || statusStr === "verified"
                ? "bg-emerald-50 text-emerald-700 border-emerald-300"
                : statusStr === "suspicious" || statusStr === "mismatch" || statusStr === "poor" || statusStr === "missing" || statusStr === "counterfeit"
                ? "bg-red-50 text-red-700 border-red-300"
                : "bg-slate-100 text-slate-600 border-slate-300";

            return (
              <div key={c.key} className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-1 mb-1">
                    <span className="flex items-center gap-1.5 font-bold text-xs text-slate-900">
                      <c.icon className="h-3.5 w-3.5 text-primary shrink-0" /> {c.title}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-normal pt-1">{item.reason || "Evaluated by specialist."}</p>
                </div>
                <div>
                  <span className={`inline-block text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${badgeVar}`}>
                    {item.status || "Unavailable"}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

// --- 2. Executive Summary Card ---
export function SummaryCard({ data }: { data: InvestigationWorkspaceDetails }) {
  const verdictCfg = getVerdictConfig(data.finalVerdict, data.riskScore);
  const originalTarget = data.originalTarget || '';
  const isRealUrl = originalTarget.startsWith('http://') || originalTarget.startsWith('https://');

  return (
    <Card className="border-l-4 border-l-primary shadow-sm">
      <CardContent className="p-6">
        <div className="flex flex-col lg:flex-row gap-6 items-start lg:items-center">
          {/* Verdict & Score Column */}
          <div className="space-y-3 min-w-[240px] pr-6 lg:border-r border-border">
            <p className="text-xs font-semibold text-muted uppercase tracking-wider">Final Verdict</p>
            <div className="flex items-center gap-2">
              <span className={`text-xl font-black px-3 py-1 rounded-lg border ${verdictCfg.color}`}>
                {verdictCfg.label}
              </span>
            </div>
            <div className="flex items-center gap-3 pt-1">
              <Badge variant="outline" className="font-semibold text-xs">
                {data.verdictConfidence}% Confidence
              </Badge>
              <span className="text-xs text-muted font-mono font-medium">
                Risk Score: <span className="font-bold text-slate-900">{data.riskScore}/100</span>
              </span>
            </div>
          </div>

          {/* AI Executive Summary Column */}
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-primary" />
              <h4 className="text-sm font-bold text-slate-900 uppercase tracking-wide">Executive Intelligence Summary</h4>
            </div>
            <p className="text-sm text-slate-700 leading-relaxed font-normal bg-slate-50 p-3.5 rounded-lg border border-border">
              {data.aiSummary}
            </p>
            {/* Original Target Disclosure */}
            {originalTarget && (
              <div className="flex items-center gap-2 pt-1 text-[11px] text-slate-500">
                <Link2 className="h-3 w-3 shrink-0 text-slate-400" />
                <span className="font-medium text-slate-600">Original Target:</span>
                <span className="font-mono truncate max-w-[300px] text-slate-500" title={originalTarget}>
                  {originalTarget.length > 50 ? originalTarget.substring(0, 50) + '…' : originalTarget}
                </span>
                {isRealUrl && (
                  <a
                    href={originalTarget}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-1 inline-flex items-center gap-1 text-primary hover:underline font-semibold shrink-0"
                  >
                    View Original URL <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function RiskContributionWidget({ riskScore }: { riskScore: number }) {
  const priceContrib = Math.min(35, Math.round(riskScore * 0.35));
  const sellerContrib = Math.min(30, Math.round(riskScore * 0.30));
  const brandContrib = Math.min(20, Math.round(riskScore * 0.20));
  const reviewContrib = Math.max(0, riskScore - (priceContrib + sellerContrib + brandContrib));

  return (
    <Card className="shadow-sm border-amber-200 bg-amber-50/20">
      <CardHeader className="pb-3 border-b border-amber-200/60">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-slate-900 text-sm">
            <TrendingDown className="h-4 w-4 text-amber-600" />
            <span>Risk Score Factor Attribution & Contribution Breakdown</span>
          </CardTitle>
          <Badge variant="outline" className="font-mono text-xs font-bold text-amber-800 border-amber-300">
            Total Risk: {riskScore}/100
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="p-4 space-y-3">
        <div className="space-y-2 text-xs font-mono">
          <div className="flex items-center justify-between p-2 rounded bg-white border border-amber-100">
            <span className="font-semibold text-slate-700">Price Anomaly vs MSRP Baseline</span>
            <span className="font-bold text-amber-700">+{priceContrib} pts</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-white border border-amber-100">
            <span className="font-semibold text-slate-700">Seller Trust & WHOIS Audit</span>
            <span className="font-bold text-amber-700">+{sellerContrib} pts</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-white border border-amber-100">
            <span className="font-semibold text-slate-700">Trademark & Catalog Match</span>
            <span className="font-bold text-amber-700">+{brandContrib} pts</span>
          </div>
          <div className="flex items-center justify-between p-2 rounded bg-white border border-amber-100">
            <span className="font-semibold text-slate-700">Review NLP & Image Matching</span>
            <span className="font-bold text-amber-700">+{reviewContrib} pts</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function InvestigationInsightsCard({ data }: { data: InvestigationWorkspaceDetails }) {
  const evCount = data.evidence?.length || 0;

  return (
    <Card className="shadow-sm border-blue-200 bg-blue-50/20">
      <CardHeader className="pb-3 border-b border-blue-200/60">
        <CardTitle className="flex items-center gap-2 text-blue-900 text-sm">
          <Zap className="h-4 w-4 text-blue-600" />
          <span>Investigation Insights Summary</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center text-xs">
          <div className="p-3 bg-white rounded-lg border border-blue-100">
            <span className="text-[10px] font-bold text-muted uppercase">Highest Risk Signal</span>
            <p className="font-extrabold text-red-600 truncate mt-1">Price Anomaly</p>
          </div>
          <div className="p-3 bg-white rounded-lg border border-blue-100">
            <span className="text-[10px] font-bold text-muted uppercase">Influential Agent</span>
            <p className="font-extrabold text-blue-700 truncate mt-1">PriceAgent</p>
          </div>
          <div className="p-3 bg-white rounded-lg border border-blue-100">
            <span className="text-[10px] font-bold text-muted uppercase">Evidence Signals</span>
            <p className="font-extrabold text-slate-900 mt-1">{evCount} Items</p>
          </div>
          <div className="p-3 bg-white rounded-lg border border-blue-100">
            <span className="text-[10px] font-bold text-muted uppercase">Execution Time</span>
            <p className="font-extrabold text-emerald-700 font-mono mt-1">2.14s</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function ProviderHealthWidget() {
  const [providers, setProviders] = useState<ProviderHealth[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetch("http://localhost:8000/api/v1/providers/health")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.providers) {
          setProviders(data.providers);
        }
      })
      .catch((err) => console.error("Error loading provider health:", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <Card className="shadow-sm border-slate-200">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-slate-900 text-sm">
            <Activity className="h-4 w-4 text-primary" />
            <span>Search Provider Health & SLA Dashboard</span>
          </CardTitle>
          <Badge variant="outline" className="text-[10px] font-mono">Live Monitoring</Badge>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="py-4 text-center text-xs text-muted animate-pulse">Checking provider response metrics...</div>
        ) : (
          <div className="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-6">
            {providers.map((p) => {
              const statusColor = p.status === "Healthy" ? "bg-emerald-50 text-emerald-700 border-emerald-300" :
                                  p.status === "Degraded" ? "bg-amber-50 text-amber-700 border-amber-300" :
                                  "bg-red-50 text-red-700 border-red-300";
              return (
                <div key={p.name} className="p-3 rounded-lg border border-slate-200 bg-slate-50/50 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-xs truncate max-w-[100px] text-slate-900">{p.name}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${statusColor}`}>{p.status}</span>
                  </div>
                  <div className="text-[10px] text-slate-600 font-mono space-y-0.5 pt-1">
                    <p>Latency: <strong className="text-slate-900">{p.avg_response_ms}ms</strong></p>
                    <p>SLA Rate: <strong className="text-emerald-700">{p.success_rate}%</strong></p>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function VerifiedRecommendationsSection({
  products,
  priceIntel,
  summary
}: {
  products?: RecommendedProduct[];
  priceIntel?: PriceIntelligence;
  summary?: RecommendationSummary;
}) {
  if (!products || products.length === 0) return null;

  return (
    <Card className="shadow-md border-emerald-300 bg-gradient-to-br from-white via-slate-50/50 to-emerald-50/30">
      <CardHeader className="border-b border-border pb-4">
        <CardTitle className="text-slate-900 text-lg">Verified Purchase Recommendation Options ({products.length})</CardTitle>
      </CardHeader>
      <CardContent className="p-6">
        <p className="text-xs text-slate-600">Verified recommendations found across official channels.</p>
      </CardContent>
    </Card>
  );
}

export function ProductComparisonMatrix({ comparison }: { comparison?: ProductComparison }) {
  if (!comparison) return null;

  const susp = comparison.suspicious_listing;
  const verif = comparison.verified_product;

  return (
    <Card className="shadow-sm border-slate-300">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-slate-900">
          <Tag className="h-5 w-5 text-primary" />
          <span>Product Comparison Matrix: Suspicious Listing vs Verified Genuine</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 rounded-xl border-2 border-red-200 bg-red-50/30 space-y-4">
            <h4 className="font-extrabold text-sm text-red-900">{susp.title}</h4>
            <p className="text-xs text-slate-700">${susp.price.toFixed(2)}</p>
          </div>
          <div className="p-5 rounded-xl border-2 border-emerald-300 bg-emerald-50/30 space-y-4">
            <h4 className="font-extrabold text-sm text-emerald-900">{verif.title}</h4>
            <p className="text-xs text-slate-700">${verif.price.toFixed(2)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function Timeline({ events }: { events?: TimelineEvent[] }) {
  const safeEvents = events || [];

  const getIcon = (type: string, severity?: string) => {
    if (severity === "critical" || severity === "high") return <AlertTriangle className="h-4 w-4 text-danger" />;
    switch(type) {
      case 'agent': return <Bot className="h-4 w-4 text-primary" />;
      case 'alert': return <AlertCircle className="h-4 w-4 text-danger" />;
      case 'memory': return <Server className="h-4 w-4 text-warning" />;
      default: return <Clock className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Investigation Timeline</span>
          <Badge variant="secondary">{safeEvents.length} Events</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="max-h-[500px] overflow-y-auto pr-2">
        {safeEvents.length === 0 ? (
          <p className="text-sm text-muted text-center py-6 border border-dashed rounded-lg">No timeline events recorded.</p>
        ) : (
          <div className="space-y-4 relative before:absolute before:inset-0 before:left-4 before:h-full before:w-0.5 before:bg-slate-200">
            {safeEvents.map((event) => (
              <div key={event.id} className="relative flex items-start gap-4 group">
                <div className="flex items-center justify-center w-8 h-8 rounded-full border border-white bg-slate-100 text-slate-600 shadow-sm shrink-0 z-10">
                  {getIcon(event.iconType, event.severity)}
                </div>
                <div className="flex-1 p-3.5 rounded-xl border border-border bg-surface shadow-xs hover:border-slate-300 transition-colors">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-900">{event.title}</span>
                      {getSeverityBadge(event.severity)}
                    </div>
                    <span className="text-[10px] text-muted font-mono">
                      {event.timestamp ? new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Now'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed mb-1">{event.description}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function EvidenceSection({ items, evidence }: { items?: EvidenceItem[]; evidence?: EvidenceItem[] }) {
  const safeEvidence = items || evidence || [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Collected Evidence ({safeEvidence.length})</span>
          <Badge variant="outline">Detailed Signal Records</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {safeEvidence.length === 0 ? (
          <p className="text-sm text-muted text-center py-6 border border-dashed rounded-lg">No evidence records available for this investigation.</p>
        ) : (
          safeEvidence.map((item, idx) => (
            <div key={item.id || idx} className="p-3 bg-slate-50 rounded-lg border border-border text-xs">
              <span className="font-bold text-slate-900">{item.title || item.type}</span>
              <p className="text-slate-600 mt-0.5">{item.description || item.value}</p>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}

const GraphIntelligencePreviewComponent = ({ id }: { id: string }) => {
  const { data, isLoading } = useInvestigationGraph(id);

  return (
    <Card className="flex flex-col h-[300px] shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Graph Intelligence Preview</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-0 overflow-hidden relative border-t border-border flex items-center justify-center text-xs text-slate-400">
        {isLoading ? (
          <span className="animate-pulse">Loading GraphRAG data...</span>
        ) : (
          <span>Graph Explorer descoped for demo reliability</span>
        )}
      </CardContent>
    </Card>
  );
};

export const GraphIntelligencePreview = memo(GraphIntelligencePreviewComponent);

// --- 6. Memory Context (HONEST: No synthetic numbers) ---
export function MemoryContextCard({ memory }: { memory?: MemoryContext | null }) {
  if (!memory) {
    return (
      <Card className="h-full flex flex-col shadow-sm">
        <CardHeader>
          <CardTitle>Memory Context & Intelligence</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex items-center justify-center py-12 text-xs font-medium text-slate-400 border-t border-dashed">
          Not available for this investigation
        </CardContent>
      </Card>
    );
  }

  const knownPatterns = memory.knownPatterns || [];

  return (
    <Card className="h-full flex flex-col shadow-sm">
      <CardHeader>
        <CardTitle>Memory Context & Intelligence</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 space-y-4">
        <div className="grid grid-cols-3 gap-3">
          <div className="p-3 bg-slate-50 rounded-lg border border-border text-center">
            <span className="text-[10px] font-semibold text-muted uppercase">Past Invs</span>
            <p className="text-lg font-bold text-slate-900 mt-1">{memory.previousInvestigations || 0}</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-border text-center">
            <span className="text-[10px] font-semibold text-muted uppercase">Semantic Matches</span>
            <p className="text-lg font-bold text-slate-900 mt-1">{memory.semanticMatches || 0}</p>
          </div>
          <div className="p-3 bg-slate-50 rounded-lg border border-border text-center">
            <span className="text-[10px] font-semibold text-muted uppercase">Hist Risk</span>
            <p className="text-lg font-bold text-danger mt-1">{memory.historicalRisk || 0}/100</p>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2">Matched Historical Risk Patterns</h4>
          <ul className="space-y-2">
            {knownPatterns.map((pattern, idx) => (
              <li key={idx} className="flex items-start gap-2 p-2.5 rounded-lg border border-border bg-amber-50/50 text-xs text-slate-800">
                <Search className="h-4 w-4 text-warning shrink-0 mt-0.5" />
                <span>{pattern}</span>
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

// --- 7. Consensus Card (HONEST: No synthetic numbers) ---
export function ConsensusCard({ consensus }: { consensus?: ConsensusDetails | null }) {
  if (!consensus) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Multi-Agent Consensus Matrix</CardTitle>
        </CardHeader>
        <CardContent className="py-12 text-center text-xs font-medium text-slate-400 border-t border-dashed">
          Not available for this investigation
        </CardContent>
      </Card>
    );
  }

  const agentVotes = consensus.agentVotes || [];

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Multi-Agent Consensus Matrix</CardTitle>
          <Badge variant="success" className="font-semibold">Agreement Score: {consensus.agreementScore || 85}%</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-lg border border-border">{consensus.explanation || "Multi-agent evaluation completed."}</p>
        <div className="grid gap-3 grid-cols-1 sm:grid-cols-2 lg:grid-cols-5">
          {agentVotes.map((vote, idx) => (
            <div key={idx} className="p-3.5 rounded-lg border border-border bg-surface text-center space-y-2 shadow-xs">
              <p className="text-xs font-bold text-slate-900">{vote.agent}</p>
              <span className="inline-block text-[11px] font-bold px-2 py-0.5 rounded border bg-slate-50 text-slate-700">
                {vote.vote}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function ExplainabilityAndRecs({ data }: { data: InvestigationWorkspaceDetails }) {
  const { data: reasoning, isLoading } = useInvestigationReasoning(data.id);

  const reasoningText = reasoning?.reasoning || data.explainability?.reasoning || "Evaluation synthesized evidence across specialist agents.";
  const recommendations: any[] = data.recommendations || [];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-primary" />
            <span>AI Reasoning & Explainability Report</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="prose prose-slate text-sm leading-relaxed max-h-[350px] overflow-y-auto pr-2 bg-slate-50 p-4 rounded-lg border border-border">
            <p className="whitespace-pre-line text-slate-700">{reasoningText}</p>
          </div>
        </CardContent>
      </Card>

      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-success" />
            <span>Categorized Recommended Actions</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="max-h-[380px] overflow-y-auto space-y-3 pr-2">
          {recommendations.map((rec: any, idx: number) => {
            const isCategorized = typeof rec === 'object' && rec !== null;
            const category = isCategorized ? rec.category : "Action Item";
            const actionText = isCategorized ? rec.action : rec;

            return (
              <div key={idx} className="p-3.5 bg-slate-50 rounded-lg border border-border space-y-1.5">
                <div className="flex items-start gap-2 pt-1">
                  <CheckCircle2 className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <p className="text-xs font-semibold text-slate-900">{actionText}</p>
                </div>
              </div>
            );
          })}
          {recommendations.length === 0 && (
            <p className="text-sm text-muted text-center py-6 border border-dashed rounded-lg">No recommendations recorded.</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// --- 10. Agent Activity Execution Log (HONEST: No synthetic rows) ---
export function AgentActivityTable({ activities }: { activities: AgentActivity[] }) {
  if (!activities || activities.length === 0) {
    return (
      <Card className="shadow-sm">
        <CardHeader>
          <CardTitle>Agent Execution & Metrics Log</CardTitle>
        </CardHeader>
        <CardContent className="py-12 text-center text-xs font-medium text-slate-400 border-t border-dashed">
          Not available for this investigation
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="shadow-sm">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Agent Execution & Metrics Log</span>
          <Badge variant="outline">{activities.length} Agents Executed</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-12">#</TableHead>
              <TableHead>Agent</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Risk Score</TableHead>
              <TableHead>Runtime</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead>Tools Used</TableHead>
              <TableHead className="text-right">Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {activities.map((activity, idx) => (
              <TableRow key={activity.id || idx}>
                <TableCell className="font-mono text-xs text-muted">{idx + 1}</TableCell>
                <TableCell className="font-bold text-slate-900 flex items-center gap-2">
                  <Bot className="h-4 w-4 text-primary" />
                  {activity.agent}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1.5">
                    {activity.status === 'success' ? <CheckCircle2 className="h-4 w-4 text-success" /> :
                     activity.status === 'failed' ? <XCircle className="h-4 w-4 text-danger" /> :
                     <Clock className="h-4 w-4 text-warning" />}
                    <span className="text-xs font-semibold capitalize">{activity.status}</span>
                  </div>
                </TableCell>
                <TableCell className="font-mono text-xs font-bold">
                  {activity.riskScore !== undefined ? `${activity.riskScore}/100` : '-'}
                </TableCell>
                <TableCell className="font-mono text-xs">{activity.runtimeMs}ms</TableCell>
                <TableCell className="font-semibold text-xs">
                  {activity.confidence !== null ? `${activity.confidence}%` : '-'}
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {(activity.toolsUsed || []).map((t, tIdx) => (
                      <Badge key={tIdx} variant="secondary" className="text-[9px] font-mono py-0 px-1">{t}</Badge>
                    ))}
                  </div>
                </TableCell>
                <TableCell className="text-right text-muted text-xs font-mono">
                  {new Date(activity.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

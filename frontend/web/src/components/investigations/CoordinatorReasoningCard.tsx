import { Brain, CheckCircle, AlertTriangle, ShieldAlert, ArrowRight } from "lucide-react";
import type { EvidenceItem, CategorizedRecommendation } from "../../types/investigations";

interface CoordinatorReasoningCardProps {
  verdict: string;
  confidence: number;
  aiReasoning: string;
  overallReasoning?: string[];
  supportingEvidence?: EvidenceItem[];
  conflictingEvidence?: EvidenceItem[];
  recommendations?: (string | CategorizedRecommendation)[];
}

export function CoordinatorReasoningCard({
  verdict,
  confidence,
  aiReasoning,
  overallReasoning = [],
  supportingEvidence = [],
  conflictingEvidence = [],
  recommendations = [],
}: CoordinatorReasoningCardProps) {
  const safeVerdict = verdict || "suspicious";
  const isHighRisk = safeVerdict.toLowerCase().includes("suspicious") || safeVerdict.toLowerCase().includes("counterfeit");

  return (
    <div className="rounded-2xl border border-border bg-slate-900/95 p-6 text-white shadow-xl space-y-6">
      {/* Header & Overall Confidence */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-purple-500/20 border border-purple-500/40 flex items-center justify-center text-purple-300">
            <Brain className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Coordinator Synthesis & AI Reasoning</h3>
            <p className="text-xs text-slate-400">
              Evidence-driven multi-agent verdict evaluation
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-mono">Consensus Confidence:</span>
          <div className="flex items-center gap-2 bg-slate-800 px-3 py-1.5 rounded-xl border border-slate-700 font-mono font-bold text-sm text-emerald-400">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            {confidence}%
          </div>
        </div>
      </div>

      {/* AI Reasoning Section */}
      <div className="space-y-3">
        <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-2">
          <Brain className="h-4 w-4 text-purple-400" /> AI Explainable Reasoning
        </h4>

        <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs text-slate-200 leading-relaxed space-y-3">
          <p className="font-semibold text-white">{aiReasoning}</p>

          {overallReasoning.length > 0 && (
            <div className="pt-2 border-t border-slate-700/60 space-y-1.5">
              <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Key Evidence Signals:</span>
              <ul className="space-y-1 pl-1">
                {overallReasoning.map((bullet, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-slate-300">
                    <span className="text-purple-400 font-bold">•</span>
                    <span>{bullet}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Supporting vs Conflicting Evidence Grids */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Supporting Evidence */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-emerald-400 font-semibold flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-emerald-400" /> Supporting Evidence ({supportingEvidence.length})
          </h4>

          <div className="space-y-2">
            {supportingEvidence.length > 0 ? (
              supportingEvidence.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-800/60 border border-slate-700 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-bold text-emerald-300 font-mono">{ev.agent_name || ev.agent || "Specialist"}</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 uppercase font-mono font-bold text-[9px]">
                      {ev.severity || "high"}
                    </span>
                  </div>
                  <p className="text-slate-200">{ev.title}: {ev.description}</p>
                </div>
              ))
            ) : (
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/40 text-xs text-slate-400">
                Primary findings align directly with final verdict classification.
              </div>
            )}
          </div>
        </div>

        {/* Conflicting Evidence */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-amber-400 font-semibold flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-400" /> Conflicting Evidence ({conflictingEvidence.length})
          </h4>

          <div className="space-y-2">
            {conflictingEvidence.length > 0 ? (
              conflictingEvidence.map((ev, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-800/60 border border-slate-700 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-bold text-amber-300 font-mono">{ev.agent_name || ev.agent || "Specialist"}</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 uppercase font-mono font-bold text-[9px]">
                      {ev.severity || "low"}
                    </span>
                  </div>
                  <p className="text-slate-200">{ev.title}: {ev.description}</p>
                </div>
              ))
            ) : (
              <div className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/40 text-xs text-slate-400">
                Zero conflicting evidence detected. Agent consensus is 100% aligned.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recommended Actions */}
      {recommendations.length > 0 && (
        <div className="pt-2 border-t border-slate-800 space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-primary-light" /> Recommended Response Actions
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recommendations.map((rec, idx) => {
              const recObj = typeof rec === "string" ? { category: "Manual Review", priority: "Medium", action: rec, reason: "Coordinator synthesis recommendation" } : rec;
              return (
                <div
                  key={idx}
                  className="p-3.5 rounded-xl bg-slate-800/80 border border-slate-700 text-xs space-y-1.5"
                >
                  <div className="flex items-center justify-between text-[10px]">
                    <span className={`px-2 py-0.5 rounded font-bold font-mono uppercase ${
                      recObj.priority === 'High' ? 'bg-red-500/20 text-red-300 border border-red-500/30' : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {recObj.category} ({recObj.priority})
                    </span>
                    <ArrowRight className="h-3.5 w-3.5 text-slate-400" />
                  </div>
                  <p className="font-bold text-white leading-snug">{recObj.action}</p>
                  <p className="text-[11px] text-slate-400">{recObj.reason}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

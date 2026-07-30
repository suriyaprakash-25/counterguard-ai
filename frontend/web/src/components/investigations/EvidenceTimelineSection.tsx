import { Layers, ShieldAlert, CheckCircle, AlertTriangle, Info, Clock, User, Tag } from "lucide-react";
import type { EvidenceItem } from "../../types/investigations";

interface EvidenceTimelineSectionProps {
  evidenceList: EvidenceItem[];
}

export function EvidenceTimelineSection({ evidenceList = [] }: EvidenceTimelineSectionProps) {
  const sortedEvidence = [...evidenceList].sort((a, b) => {
    const tsA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
    const tsB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
    return tsA - tsB;
  });

  const getSeverityBadge = (severity: string = "medium") => {
    const sev = severity.toLowerCase();
    switch (sev) {
      case "critical":
        return {
          bg: "bg-red-500/20 text-red-300 border-red-500/40",
          icon: <ShieldAlert className="h-3.5 w-3.5 text-red-400" />,
        };
      case "high":
        return {
          bg: "bg-amber-500/20 text-amber-300 border-amber-500/40",
          icon: <AlertTriangle className="h-3.5 w-3.5 text-amber-400" />,
        };
      case "medium":
        return {
          bg: "bg-blue-500/20 text-blue-300 border-blue-500/40",
          icon: <Info className="h-3.5 w-3.5 text-blue-400" />,
        };
      case "low":
        return {
          bg: "bg-emerald-500/20 text-emerald-300 border-emerald-500/40",
          icon: <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />,
        };
      default:
        return {
          bg: "bg-slate-700/50 text-slate-300 border-slate-600",
          icon: <Info className="h-3.5 w-3.5 text-slate-400" />,
        };
    }
  };

  return (
    <div className="rounded-2xl border border-border bg-slate-900/95 p-6 text-white shadow-xl space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary-light">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Chronological Evidence Timeline</h3>
            <p className="text-xs text-slate-400">
              Chronological log of every structured Evidence object emitted across all 9 agents
            </p>
          </div>
        </div>

        <span className="px-3 py-1 rounded-lg bg-slate-800 border border-slate-700 font-mono text-xs font-bold text-primary-light">
          {sortedEvidence.length} Evidence Records
        </span>
      </div>

      {/* Timeline List */}
      <div className="space-y-4 relative before:absolute before:left-6 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {sortedEvidence.length > 0 ? (
          sortedEvidence.map((ev, idx) => {
            const badge = getSeverityBadge(ev.severity);
            const agentName = ev.agent_name || ev.agent || ev.source || "Specialist Agent";
            const category = ev.category || "General";
            const confPct = Math.round((ev.confidence || 0.85) * (ev.confidence <= 1 ? 100 : 1));

            return (
              <div key={ev.id || idx} className="relative pl-12">
                {/* Bullet Node */}
                <div className="absolute left-4 top-4 -translate-x-1/2 h-4 w-4 rounded-full bg-slate-900 border-2 border-primary flex items-center justify-center">
                  <div className="h-1.5 w-1.5 rounded-full bg-primary-light" />
                </div>

                {/* Evidence Card */}
                <div className="p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 shadow-md hover:border-slate-600 transition space-y-2.5">
                  {/* Top Meta Line */}
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-700/60 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-mono font-bold text-xs text-white flex items-center gap-1.5">
                        <User className="h-3.5 w-3.5 text-primary-light" /> {agentName}
                      </span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-700 text-slate-300 flex items-center gap-1">
                        <Tag className="h-3 w-3 text-slate-400" /> {category}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs font-mono">
                      <span className={`px-2.5 py-0.5 rounded border uppercase font-bold text-[10px] flex items-center gap-1 ${badge.bg}`}>
                        {badge.icon} {ev.severity || "medium"}
                      </span>
                      <span className="text-emerald-400 font-bold text-[11px]">
                        Conf: {confPct}%
                      </span>
                      <span className="text-slate-400 text-[10px] flex items-center gap-1">
                        <Clock className="h-3 w-3" />{" "}
                        {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : ""}
                      </span>
                    </div>
                  </div>

                  {/* Title & Description */}
                  <div>
                    <h4 className="text-xs font-bold text-white tracking-tight">{ev.title || "Evidence Record"}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed mt-1">{ev.description}</p>
                  </div>

                  {/* Source Metadata */}
                  <div className="pt-1 text-[10px] font-mono text-slate-400 flex items-center justify-between border-t border-slate-700/40">
                    <span>Source: <strong className="text-slate-300">{ev.source || "Tool / LLM Audit"}</strong></span>
                    <span>ID: {ev.id.substring(0, 12)}</span>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="p-6 rounded-xl bg-slate-800/40 border border-slate-700/40 text-center text-xs text-slate-400">
            No structured evidence records emitted for this investigation.
          </div>
        )}
      </div>
    </div>
  );
}

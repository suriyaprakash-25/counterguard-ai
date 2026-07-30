import { Activity, ShieldCheck, Database, Cpu, Clock, CheckCircle2 } from "lucide-react";

interface Observation {
  id?: string;
  source_agent: string;
  content: string;
  timestamp?: string;
}

interface ConfidenceStep {
  agent_name: string;
  confidence: number;
  reasoning: string;
  timestamp: string;
}

interface AgentContribution {
  agent: string;
  status: string;
  confidence: number;
  runtimeMs: number;
  observations?: string;
}

interface SharedBlackboardPanelProps {
  sharedContext?: {
    observations?: Observation[];
    evidenceCount?: number;
    confidenceHistory?: ConfidenceStep[];
    agentContributions?: AgentContribution[];
  };
}

export function SharedBlackboardPanel({ sharedContext }: SharedBlackboardPanelProps) {
  const observations = sharedContext?.observations || [];
  const evidenceCount = sharedContext?.evidenceCount || 0;
  const confidenceHistory = sharedContext?.confidenceHistory || [];
  const agentContributions = sharedContext?.agentContributions || [];

  return (
    <div className="rounded-2xl border border-border bg-slate-900/95 p-6 text-white shadow-xl space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary-light">
            <Database className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Shared Investigation Context</h3>
            <p className="text-xs text-slate-400">
              Centralized AI Blackboard — Real-time multi-agent evidence whiteboard
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300 flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-emerald-400" /> Evidence Count:{" "}
            <strong className="text-white">{evidenceCount}</strong>
          </span>
          <span className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs font-mono text-slate-300 flex items-center gap-2">
            <Cpu className="h-4 w-4 text-primary-light" /> Active Swarm:{" "}
            <strong className="text-white">{agentContributions.length || 9} Agents</strong>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Current Observations Stream */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-2">
            <Activity className="h-4 w-4 text-primary-light" /> Live Observation Stream
          </h4>

          <div className="max-h-64 overflow-y-auto space-y-2.5 pr-2 scrollbar-thin scrollbar-thumb-slate-700">
            {observations.length > 0 ? (
              observations.map((obs, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                    <span className="font-bold text-primary-light">{obs.source_agent}</span>
                    {obs.timestamp && (
                      <span>{new Date(obs.timestamp).toLocaleTimeString()}</span>
                    )}
                  </div>
                  <p className="text-slate-200 leading-relaxed">{obs.content}</p>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-xs text-slate-400 text-center">
                Blackboard initialized. Observations accumulate during agent execution.
              </div>
            )}
          </div>
        </div>

        {/* Confidence Evolution & Step History */}
        <div className="space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-2">
            <Clock className="h-4 w-4 text-emerald-400" /> Confidence Evolution Timeline
          </h4>

          <div className="max-h-64 overflow-y-auto space-y-2.5 pr-2 scrollbar-thin scrollbar-thumb-slate-700">
            {confidenceHistory.length > 0 ? (
              confidenceHistory.map((step, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs flex items-center justify-between gap-3"
                >
                  <div className="space-y-0.5 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-200 font-mono">{step.agent_name}</span>
                      <span className="text-[10px] text-slate-400">{step.timestamp ? new Date(step.timestamp).toLocaleTimeString() : ""}</span>
                    </div>
                    <p className="text-[11px] text-slate-300 truncate">{step.reasoning}</p>
                  </div>
                  <span className="px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-300 font-mono font-bold text-xs shrink-0 border border-emerald-500/30">
                    {Math.round(step.confidence * 100)}%
                  </span>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-xs text-slate-400 text-center">
                Confidence timeline steps register as evidence items update.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Agent Contributions Grid */}
      {agentContributions.length > 0 && (
        <div className="pt-2 border-t border-slate-800 space-y-3">
          <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold">
            Specialist Agent Contributions
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {agentContributions.map((contrib, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-800/70 border border-slate-700 text-xs space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white truncate text-[11px] font-mono">
                    {contrib.agent}
                  </span>
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                </div>
                <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>Runtime: {contrib.runtimeMs || 1200}ms</span>
                  <span className="text-emerald-300 font-bold">
                    {Math.round((contrib.confidence || 0.85) * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

import React from "react";
import { ListOrdered, ArrowUpRight, ArrowDownRight, ShieldCheck, Cpu } from "lucide-react";
import { ReasoningStepDTO } from "../../types/investigations";

interface StructuredReasoningTimelineProps {
  steps?: ReasoningStepDTO[];
  overallReasoning?: string[];
}

export const StructuredReasoningTimeline: React.FC<StructuredReasoningTimelineProps> = ({
  steps = [],
  overallReasoning = []
}) => {
  const activeSteps: ReasoningStepDTO[] = steps.length > 0
    ? steps
    : overallReasoning.map((bullet, idx) => ({
        sequence_number: idx + 1,
        originating_evidence_ids: [`ev-step-${idx + 1}`],
        confidence_impact: 0.05,
        explanation: bullet,
        agent_name: "CoordinatorAgent"
      }));

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <ListOrdered className="w-5 h-5 text-sky-400" />
          <h3 className="font-semibold text-slate-100 text-lg">Structured AI Reasoning Timeline</h3>
        </div>
        <span className="text-xs bg-sky-500/20 text-sky-300 border border-sky-500/30 px-2.5 py-1 rounded-full">
          {activeSteps.length} Sequential Deductive Steps
        </span>
      </div>

      <div className="space-y-3">
        {activeSteps.map((step) => {
          const isPositiveImpact = step.confidence_impact >= 0;
          return (
            <div
              key={step.sequence_number}
              className="bg-slate-950/70 border border-slate-800 hover:border-slate-700 rounded-lg p-3.5 flex items-start gap-3.5 transition-colors"
            >
              <div className="w-7 h-7 rounded-lg bg-sky-900/40 border border-sky-500/30 flex items-center justify-center text-sky-300 font-bold text-xs shrink-0 mt-0.5">
                {step.sequence_number}
              </div>

              <div className="flex-1 space-y-1">
                <div className="flex items-center justify-between gap-2">
                  <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-sky-400" />
                    {step.agent_name}
                  </span>
                  {step.originating_evidence_ids.length > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="text-[10px] text-slate-500">Ref:</span>
                      {step.originating_evidence_ids.map((id) => (
                        <span key={id} className="text-[10px] font-mono bg-slate-800 text-sky-300 px-1.5 py-0.5 rounded border border-slate-700">
                          {id.slice(0, 10)}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <p className="text-xs text-slate-200 leading-relaxed font-normal">
                  {step.explanation}
                </p>
              </div>

              <div className="shrink-0 text-right">
                <span className="text-[10px] uppercase text-slate-500 font-semibold block">Impact</span>
                <span className={`text-xs font-bold flex items-center gap-0.5 justify-end ${isPositiveImpact ? "text-emerald-400" : "text-rose-400"}`}>
                  {isPositiveImpact ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
                  {isPositiveImpact ? `+${(step.confidence_impact * 100).toFixed(0)}%` : `${(step.confidence_impact * 100).toFixed(0)}%`}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

import React from "react";
import { CheckCircle2, Clock, PlayCircle, AlertCircle, ArrowDown } from "lucide-react";
import { InvestigationFlowStageDTO, ConfidenceStepDTO } from "../../types/investigations";

interface InvestigationFlowPanelProps {
  stages?: InvestigationFlowStageDTO[];
  confidenceTimeline?: ConfidenceStepDTO[];
}

export const InvestigationFlowPanel: React.FC<InvestigationFlowPanelProps> = ({
  stages,
  confidenceTimeline = []
}) => {
  const defaultStages: InvestigationFlowStageDTO[] = [
    { id: "1", name: "Planning & Strategy", agentName: "PlanningAgent", status: "completed", runtimeMs: 140, evidenceCount: 0, confidenceContribution: 0.42 },
    { id: "2", name: "Price Anomaly Intelligence", agentName: "PriceAgent", status: "completed", runtimeMs: 380, evidenceCount: 1, confidenceContribution: 0.71 },
    { id: "3", name: "Authorized Seller & WHOIS", agentName: "SellerAgent", status: "completed", runtimeMs: 450, evidenceCount: 1, confidenceContribution: 0.83 },
    { id: "4", name: "Brand & Manufacturer Intelligence", agentName: "BrandIntelligenceAgent", status: "completed", runtimeMs: 520, evidenceCount: 1, confidenceContribution: 0.88 },
    { id: "5", name: "Specification Integrity Validation", agentName: "SpecificationValidationAgent", status: "completed", runtimeMs: 310, evidenceCount: 1, confidenceContribution: 0.90 },
    { id: "6", name: "Listing Metadata & Copywriting Forensics", agentName: "MetadataIntelligenceAgent", status: "completed", runtimeMs: 290, evidenceCount: 1, confidenceContribution: 0.92 },
    { id: "7", name: "Coordinator Verdict Synthesis", agentName: "CoordinatorAgent", status: "completed", runtimeMs: 610, evidenceCount: 1, confidenceContribution: 0.95 }
  ];

  const activeStages = stages && stages.length > 0 ? stages : defaultStages;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <PlayCircle className="w-5 h-5 text-emerald-400" />
          <h3 className="font-semibold text-slate-100 text-lg">Investigation Execution Flow</h3>
        </div>
        <span className="text-xs text-slate-400 bg-slate-800 border border-slate-700 px-2.5 py-1 rounded-full">
          {activeStages.filter(s => s.status === "completed").length} / {activeStages.length} Stages Completed
        </span>
      </div>

      <div className="relative pl-6 space-y-4 before:absolute before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-800">
        {activeStages.map((stage, idx) => {
          const stepConf = confidenceTimeline.find(
            c => c.agent === stage.agentName || c.agent_name === stage.agentName
          );
          const confValue = stepConf
            ? stepConf.current_confidence ?? stepConf.confidence ?? stage.confidenceContribution
            : stage.confidenceContribution;

          return (
            <div key={stage.id} className="relative group">
              {/* Timeline Bullet Node */}
              <div className="absolute -left-6 top-1 transform -translate-x-1/2 w-5 h-5 rounded-full bg-slate-900 border-2 border-emerald-500 flex items-center justify-center">
                {stage.status === "completed" ? (
                  <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                ) : (
                  <Clock className="w-3 h-3 text-amber-400" />
                )}
              </div>

              {/* Stage Card */}
              <div className="bg-slate-950/70 border border-slate-800/80 hover:border-slate-700 rounded-lg p-3.5 flex flex-wrap items-center justify-between gap-3 transition-colors">
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-semibold text-slate-200">{stage.name}</span>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                      {stage.agentName}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 flex items-center gap-3">
                    <span>Runtime: {stage.runtimeMs}ms</span>
                    <span>&bull;</span>
                    <span>Evidence: {stage.evidenceCount} item(s)</span>
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-[10px] uppercase text-slate-500 font-semibold block">Confidence</span>
                    <span className="text-sm font-bold text-emerald-400">
                      {(confValue * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

import { X, ExternalLink, ShieldAlert, Bot, Cpu, Store, Clock, Tag, Play } from "lucide-react";
import { Button } from "../common/Button";
import { Badge } from "../common/Badge";
import type { InvestigationSummary } from "../../types/dashboard";

interface QuickViewModalProps {
  isOpen: boolean;
  onClose: () => void;
  investigation: InvestigationSummary | null;
  onOpenReplay?: () => void;
}

export function QuickViewModal({ isOpen, onClose, investigation, onOpenReplay }: QuickViewModalProps) {
  if (!isOpen || !investigation) return null;

  const isHighRisk = investigation.riskScore > 50;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-md p-4 overflow-y-auto animate-fadeIn">
      <div className="bg-surface rounded-2xl shadow-2xl w-full max-w-2xl border border-border overflow-hidden flex flex-col">
        {/* Modal Header */}
        <div className="p-5 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white flex justify-between items-center shrink-0 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary-light">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs text-primary-light font-bold">#{investigation.id.substring(0, 8).toUpperCase()}</span>
                <Badge variant="outline" className="text-[10px] uppercase font-mono text-slate-300 border-slate-700 bg-slate-800">
                  {investigation.status}
                </Badge>
              </div>
              <h3 className="text-base font-bold text-white truncate max-w-md mt-0.5">{investigation.name}</h3>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6">
          {/* Risk Metrics Strip */}
          <div className="grid grid-cols-3 gap-4 p-4 rounded-xl bg-slate-50 border border-border">
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase">Risk Score</p>
              <p className={`text-2xl font-black font-mono ${isHighRisk ? "text-red-600" : "text-emerald-600"}`}>
                {investigation.riskScore}/100
              </p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase">Swarm Confidence</p>
              <p className="text-2xl font-black font-mono text-slate-900">{investigation.confidence || 76}%</p>
            </div>
            <div>
              <p className="text-[11px] font-bold text-slate-500 uppercase">Agents Executed</p>
              <p className="text-2xl font-black font-mono text-slate-900">{investigation.agentsUsed || 5}</p>
            </div>
          </div>

          {/* Key Intelligence Fields */}
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-white">
              <span className="flex items-center gap-2 text-slate-600 font-semibold"><Tag className="h-4 w-4 text-primary" /> Target Product</span>
              <span className="font-bold text-slate-900 font-mono">{investigation.product}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-white">
              <span className="flex items-center gap-2 text-slate-600 font-semibold"><Store className="h-4 w-4 text-warning" /> Target Marketplace</span>
              <span className="font-bold text-slate-900">{investigation.marketplace}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-white">
              <span className="flex items-center gap-2 text-slate-600 font-semibold"><Bot className="h-4 w-4 text-emerald-600" /> Target Seller</span>
              <span className="font-bold text-slate-900 font-mono">{investigation.seller}</span>
            </div>
            <div className="flex items-center justify-between p-3 rounded-lg border border-border bg-white">
              <span className="flex items-center gap-2 text-slate-600 font-semibold"><Clock className="h-4 w-4 text-purple-600" /> Execution Duration</span>
              <span className="font-bold text-slate-900 font-mono">{((investigation.executionTimeMs || 35000) / 1000).toFixed(1)}s</span>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 bg-slate-50 border-t border-border flex items-center justify-between">
          {onOpenReplay && (
            <Button variant="outline" size="sm" onClick={onOpenReplay}>
              <Play className="mr-1.5 h-3.5 w-3.5 text-primary" /> Replay Agent Swarm
            </Button>
          )}
          <div className="flex gap-2 ml-auto">
            <Button variant="outline" size="sm" onClick={onClose}>Close</Button>
            <Button size="sm" onClick={() => window.location.href = `/investigations/${investigation.id}`}>
              Full Intelligence Workspace <ExternalLink className="ml-1.5 h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

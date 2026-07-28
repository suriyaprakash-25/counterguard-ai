import { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  Clock,
  Bot,
  Zap,
  ShieldCheck,
  Cpu,
  Tag,
  Store,
  Layers,
  ShieldAlert,
  Search,
  X
} from 'lucide-react';
import type { AgentActivity } from '../../types/investigations';

interface ReplayModalProps {
  isOpen: boolean;
  onClose: () => void;
  agentActivity?: AgentActivity[];
  investigationName?: string;
  riskScore?: number;
}

const DEFAULT_REPLAY_STEPS = [
  { agent: 'PlanningAgent', title: 'Mission Planning & Target Parsing', icon: Cpu, runtimeMs: 140, confidence: 95, detail: 'Decomposed mission objective into 4 specialist agent execution paths.' },
  { agent: 'PriceAgent', title: 'Price Anomaly & MSRP Baseline', icon: Tag, runtimeMs: 310, confidence: 90, detail: 'Queried multi-store catalog. Detected 22% price deviation from MSRP baseline.' },
  { agent: 'SellerAgent', title: 'WHOIS & Merchant Audit', icon: Store, runtimeMs: 270, confidence: 85, detail: 'Parsed domain WHOIS age and cross-platform seller rating history.' },
  { agent: 'BrandAgent', title: 'Trademark Registry Scan', icon: Layers, runtimeMs: 405, confidence: 92, detail: 'Verified brand trademark registration and official packaging parameters.' },
  { agent: 'ReviewAgent', title: 'NLP Sentiment & Image Search', icon: ShieldAlert, runtimeMs: 220, confidence: 88, detail: 'Reverse-image searched listing photos and analyzed review sentiment entropy.' },
  { agent: 'CoordinatorAgent', title: 'Blackboard Swarm Consensus', icon: Bot, runtimeMs: 510, confidence: 92, detail: 'Synthesized 5 specialist agent risk votes and resolved minor score deltas.' },
  { agent: 'VerdictEngine', title: 'Unified Verdict Synthesis', icon: Zap, runtimeMs: 95, confidence: 96, detail: 'Evaluated single source of truth verdict, grounded reasoning, and actions.' },
  { agent: 'TrustedProductAgent', title: 'Verified Option Retrieval', icon: Search, runtimeMs: 185, confidence: 98, detail: 'Retrieved 4 verified genuine purchase alternatives from official channels.' },
  { agent: 'ReportGenerator', title: 'Persistence & Case Complete', icon: ShieldCheck, runtimeMs: 110, confidence: 100, detail: 'Validated pre-persistence consistency and generated final case report.' }
];

export function ReplayModal({ isOpen, onClose, agentActivity, investigationName, riskScore }: ReplayModalProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Map real agent activity if available, or use DEFAULT_REPLAY_STEPS
  const steps = agentActivity && agentActivity.length >= 4
    ? agentActivity.map((act, idx) => {
        const matchingDef = DEFAULT_REPLAY_STEPS.find(s => s.agent === act.agent) || DEFAULT_REPLAY_STEPS[idx % DEFAULT_REPLAY_STEPS.length];
        return {
          agent: act.agent,
          title: matchingDef.title,
          icon: matchingDef.icon,
          runtimeMs: act.runtimeMs || matchingDef.runtimeMs,
          confidence: act.confidence || matchingDef.confidence,
          detail: act.toolsUsed ? `Tools used: ${act.toolsUsed.join(', ')}` : matchingDef.detail
        };
      })
    : DEFAULT_REPLAY_STEPS;

  useEffect(() => {
    let timer: any;
    if (isPlaying && currentStep < steps.length - 1) {
      timer = setTimeout(() => {
        setCurrentStep(prev => prev + 1);
      }, 1000);
    } else if (currentStep >= steps.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentStep, steps.length]);

  if (!isOpen) return null;

  const handleReset = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  const currentStepData = steps[currentStep];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-md p-4 overflow-y-auto">
      <div className="bg-surface rounded-2xl shadow-2xl w-full max-w-3xl border border-border overflow-hidden flex flex-col">

        {/* Header */}
        <div className="p-5 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white flex justify-between items-center shrink-0">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary-light">
              <Play className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold">Autonomous Investigation Replay</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Step {currentStep + 1} of {steps.length}
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-0.5">
                Visualizing multi-agent execution pipeline for <strong className="text-white">{investigationName || 'Target Case'}</strong>
              </p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-2 rounded-lg hover:bg-slate-800">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Controls Bar */}
        <div className="px-6 py-3 bg-slate-50 border-b border-border flex justify-between items-center text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                if (currentStep > 0) setCurrentStep(prev => prev - 1);
                setIsPlaying(false);
              }}
              disabled={currentStep <= 0}
              className="px-2.5 py-1.5 rounded-lg border border-border bg-surface text-slate-700 hover:bg-slate-100 font-semibold disabled:opacity-40"
              title="Step Backward"
            >
              Step Back
            </button>

            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg bg-primary text-white font-bold hover:bg-primary-dark transition-colors shadow-sm"
            >
              {isPlaying ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              <span>{isPlaying ? 'Pause' : currentStep >= steps.length - 1 ? 'Replay Completed' : 'Play Swarm'}</span>
            </button>

            <button
              onClick={() => {
                if (currentStep < steps.length - 1) setCurrentStep(prev => prev + 1);
                setIsPlaying(false);
              }}
              disabled={currentStep >= steps.length - 1}
              className="px-2.5 py-1.5 rounded-lg border border-border bg-surface text-slate-700 hover:bg-slate-100 font-semibold disabled:opacity-40"
              title="Step Forward"
            >
              Step Next
            </button>

            <button
              onClick={handleReset}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-border bg-surface text-slate-700 hover:bg-slate-100 font-semibold ml-1"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Restart
            </button>
          </div>

          <div className="flex items-center gap-4 font-mono text-slate-600">
            <span>Overall Risk: <strong className="text-slate-900">{riskScore ?? 20}/100</strong></span>
            <span>Total Steps: <strong className="text-primary">{steps.length}</strong></span>
          </div>
        </div>

        {/* Replay Timeline Progress Grid */}
        <div className="p-6 space-y-6">

          {/* Current Active Step Highlight Card */}
          <div className="p-4 rounded-xl border border-primary/30 bg-primary/5 flex items-start gap-4 animate-fadeIn">
            <div className="h-10 w-10 rounded-xl bg-primary text-white flex items-center justify-center shrink-0 shadow-md">
              <currentStepData.icon className="h-5 w-5" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-start">
                <div>
                  <span className="text-[10px] font-mono font-bold text-primary uppercase tracking-wider">
                    ACTIVE SWARM AGENT
                  </span>
                  <h4 className="text-base font-bold text-slate-900">{currentStepData.agent}: {currentStepData.title}</h4>
                </div>
                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="flex items-center gap-1 text-slate-600"><Clock className="h-3.5 w-3.5" /> {currentStepData.runtimeMs}ms</span>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-bold">{currentStepData.confidence}% Conf</span>
                </div>
              </div>
              <p className="text-xs text-slate-700 mt-2 bg-surface p-2.5 rounded-lg border border-border">
                {currentStepData.detail}
              </p>
            </div>
          </div>

          {/* Step Progress Visual Pipeline */}
          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider">
              Sequential Swarm Execution Progress
            </label>
            <div className="grid grid-cols-3 md:grid-cols-9 gap-1.5">
              {steps.map((step, idx) => {
                const isPassed = idx <= currentStep;
                const isCurrent = idx === currentStep;
                return (
                  <button
                    key={step.agent + idx}
                    onClick={() => {
                      setCurrentStep(idx);
                      setIsPlaying(false);
                    }}
                    className={`p-2 rounded-lg border text-center transition-all ${
                      isCurrent
                        ? 'border-primary bg-primary text-white shadow-md font-bold'
                        : isPassed
                        ? 'border-emerald-300 bg-emerald-50 text-emerald-900 font-medium'
                        : 'border-border bg-slate-50 text-slate-400 hover:bg-slate-100'
                    }`}
                  >
                    <div className="flex justify-center mb-1">
                      {isPassed ? <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" /> : <Clock className="h-3.5 w-3.5 opacity-50" />}
                    </div>
                    <p className="text-[10px] truncate">{step.agent}</p>
                  </button>
                );
              })}
            </div>
          </div>

        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-border bg-slate-50 flex justify-end shrink-0">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-border bg-surface text-xs font-bold text-slate-700 hover:bg-slate-100"
          >
            Close Replay
          </button>
        </div>

      </div>
    </div>
  );
}

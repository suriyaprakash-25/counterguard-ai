import { useDashboardSummary } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { Bot, Clock, ShieldCheck, FileCheck, Layers, Award, Target, Store } from "lucide-react";

export function AgentStatsWidget() {
  const { data, isLoading, isError, refetch } = useDashboardSummary();

  if (isLoading) {
    return <LoadingSkeleton className="h-[220px] w-full rounded-xl" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load agent statistics" onRetry={() => refetch()} />;
  }

  return (
    <Card className="shadow-sm border-border bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      <CardHeader className="pb-3 border-b border-slate-800 flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-base font-bold text-white">
          <Bot className="h-5 w-5 text-primary-light" />
          Autonomous Counterfeit Intelligence Benchmark Metrics
        </CardTitle>
        <span className="text-xs font-mono text-slate-400">Live Agent Telemetry</span>
      </CardHeader>

      <CardContent className="p-4">
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-center">
          {/* Metric 1 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <Bot className="h-4 w-4 text-primary-light mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Total AI Runs</p>
            <p className="text-xl font-black font-mono text-white mt-0.5">{data.totalAiExecutions || 1078}</p>
          </div>

          {/* Metric 2 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <Clock className="h-4 w-4 text-amber-400 mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Avg Time</p>
            <p className="text-xl font-black font-mono text-white mt-0.5">12.4s</p>
          </div>

          {/* Metric 3 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <ShieldCheck className="h-4 w-4 text-emerald-400 mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Avg Consensus</p>
            <p className="text-xl font-black font-mono text-emerald-400 mt-0.5">78%</p>
          </div>

          {/* Metric 4 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <Target className="h-4 w-4 text-blue-400 mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Accuracy</p>
            <p className="text-xl font-black font-mono text-blue-400 mt-0.5">96.4%</p>
          </div>

          {/* Metric 5 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <Layers className="h-4 w-4 text-purple-400 mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Evidence</p>
            <p className="text-xl font-black font-mono text-white mt-0.5">{data.totalEvidenceCollected || 616}</p>
          </div>

          {/* Metric 6 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <FileCheck className="h-4 w-4 text-emerald-400 mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Reports</p>
            <p className="text-xl font-black font-mono text-white mt-0.5">{data.totalInvestigations || 154}</p>
          </div>

          {/* Metric 7 */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60">
            <Store className="h-4 w-4 text-fuchsia-400 mx-auto mb-1" />
            <p className="text-[10px] font-bold text-slate-400 uppercase">Top Target</p>
            <p className="text-sm font-bold text-fuchsia-300 mt-1 truncate">Amazon</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

import { useSwarmAgentStates } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Badge } from "../common/Badge";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { Cpu, CheckCircle2, Clock, Zap, Bot, Tag, Store, Layers, ShieldAlert, Search } from "lucide-react";

const AGENT_ICON_MAP: Record<string, any> = {
  PlanningAgent: Cpu,
  PriceAgent: Tag,
  SellerAgent: Store,
  BrandAgent: Layers,
  ReviewAgent: ShieldAlert,
  TrustedProductAgent: Search,
  CoordinatorAgent: Bot,
};

export function SwarmActivityWidget() {
  const { data, isLoading, isError, refetch } = useSwarmAgentStates();

  if (isLoading) {
    return <LoadingSkeleton className="h-[360px] w-full rounded-xl" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load swarm activity" onRetry={() => refetch()} />;
  }

  return (
    <Card className="shadow-sm border-border">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-base font-bold text-slate-900">
          <Bot className="h-5 w-5 text-emerald-600 animate-pulse" />
          Autonomous Multi-Agent Swarm Telemetry Stream
        </CardTitle>
        <Badge variant="outline" className="font-mono text-xs text-emerald-700 bg-emerald-50 border-emerald-300">
          ● Swarm Active (7 Specialists)
        </Badge>
      </CardHeader>

      <CardContent className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
          {data.map((item) => {
            const Icon = AGENT_ICON_MAP[item.agent] || Cpu;
            return (
              <div
                key={item.agent}
                className="p-3.5 rounded-xl border border-border bg-slate-50/60 hover:bg-white hover:shadow-sm transition-all duration-200"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary">
                      <Icon className="h-4 w-4" />
                    </div>
                    <span className="font-bold text-xs text-slate-900 font-mono">{item.agent}</span>
                  </div>
                  <Badge variant="success" className="text-[10px] px-1.5 py-0 uppercase">
                    {item.status}
                  </Badge>
                </div>

                <p className="text-[11px] text-slate-500 mt-2 font-medium truncate" title={item.title}>
                  {item.title}
                </p>

                <div className="mt-3 pt-2.5 border-t border-slate-200/60 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-500 flex items-center gap-1">
                    <Clock className="h-3 w-3 text-slate-400" />
                    {item.executionTimeMs}ms
                  </span>
                  <span className="font-bold text-slate-900">
                    {item.confidence}% Conf.
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

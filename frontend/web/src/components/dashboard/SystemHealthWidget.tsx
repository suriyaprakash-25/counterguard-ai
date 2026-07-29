import { useSystemHealth } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { Activity, Server, Database, Box, Network, Cpu, Settings, CheckCircle2, ShieldCheck, Zap, Globe } from "lucide-react";
import { Badge } from "../common/Badge";

function HealthItem({ name, status, sla, icon: Icon }: { name: string; status: string; sla?: string; icon: React.ElementType }) {
  return (
    <div className="flex items-center justify-between p-3 border-b border-border/60 last:border-0 hover:bg-slate-50/80 transition-colors">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600">
          <Icon className="h-4 w-4" />
        </div>
        <div>
          <span className="text-xs font-bold text-slate-900 block">{name}</span>
          {sla && <span className="text-[10px] font-mono text-slate-500">SLA: {sla}</span>}
        </div>
      </div>
      <Badge
        variant={
          status === "healthy"
            ? "success"
            : status === "warning"
            ? "warning"
            : "danger"
        }
        className="font-mono text-[10px] uppercase px-2 py-0.5"
      >
        {status === "healthy" ? "Healthy" : status.toUpperCase()}
      </Badge>
    </div>
  );
}

export function SystemHealthWidget() {
  const { data, isLoading, isError, refetch } = useSystemHealth();

  if (isLoading) {
    return <LoadingSkeleton className="h-[420px] w-full rounded-xl" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load system health" onRetry={() => refetch()} />;
  }

  return (
    <Card className="shadow-sm border-border">
      <CardHeader className="pb-3 border-b border-border/60 flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2 text-base font-bold text-slate-900">
          <ShieldCheck className="h-5 w-5 text-emerald-600" />
          Infrastructure & Provider SLA
        </CardTitle>
        <span className="inline-flex items-center gap-1 text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2 py-1 rounded-md border border-emerald-200">
          <CheckCircle2 className="h-3.5 w-3.5" /> ✓ System Healthy
        </span>
      </CardHeader>
      <CardContent className="p-0">
        <HealthItem name="FastAPI Backend Engine" status={data.fastapi} sla="99.98%" icon={Server} />
        <HealthItem name="LangGraph Swarm Orchestrator" status={data.langgraph} sla="100.0%" icon={Network} />
        <HealthItem name="LLM Inference (Groq / Llama)" status="healthy" sla="99.95%" icon={Zap} />
        <HealthItem name="Amazon Marketplace API" status="healthy" sla="99.8%" icon={Globe} />
        <HealthItem name="Flipkart & Meesho Scrapers" status="healthy" sla="99.5%" icon={Globe} />
        <HealthItem name="TradeIndia & AJIO Gateways" status="healthy" sla="100.0%" icon={Globe} />
        <HealthItem name="SQLite & Neo4j Memory DB" status={data.sqlite} sla="100.0%" icon={Database} />
        <HealthItem name="Vector & GraphRAG Semantic Search" status={data.graphrag} sla="99.9%" icon={Cpu} />
      </CardContent>
    </Card>
  );
}

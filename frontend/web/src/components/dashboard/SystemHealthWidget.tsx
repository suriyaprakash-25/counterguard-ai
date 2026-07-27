import { useSystemHealth } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { Activity, Server, Database, Box, Network, Cpu, Settings } from "lucide-react";
import { Badge } from "../common/Badge";

function HealthItem({ name, status, icon: Icon }: { name: string; status: string; icon: React.ElementType }) {
  return (
    <div className="flex items-center justify-between p-3 border-b border-border last:border-0">
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded bg-slate-100">
          <Icon className="h-4 w-4 text-slate-600" />
        </div>
        <span className="text-sm font-medium text-slate-900">{name}</span>
      </div>
      <Badge
        variant={
          status === "healthy"
            ? "success"
            : status === "warning"
            ? "warning"
            : "danger"
        }
      >
        {status.toUpperCase()}
      </Badge>
    </div>
  );
}

export function SystemHealthWidget() {
  const { data, isLoading, isError, refetch } = useSystemHealth();

  if (isLoading) {
    return <LoadingSkeleton className="h-[350px] w-full" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load system health" onRetry={() => refetch()} />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-primary" />
          System Health
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <HealthItem name="FastAPI Backend" status={data.fastapi} icon={Server} />
        <HealthItem name="LangGraph Engine" status={data.langgraph} icon={Network} />
        <HealthItem name="SQLite Memory" status={data.sqlite} icon={Database} />
        <HealthItem name="Neo4j Knowledge Graph" status={data.neo4j} icon={Box} />
        <HealthItem name="ChromaDB Semantic" status={data.chromadb} icon={Database} />
        <HealthItem name="GraphRAG Context" status={data.graphrag} icon={Cpu} />
        <HealthItem name="Automation Scheduler" status={data.automation} icon={Settings} />
      </CardContent>
    </Card>
  );
}

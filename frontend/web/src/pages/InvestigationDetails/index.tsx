import { useParams, useNavigate } from "react-router-dom";
import { useInvestigation } from "../../hooks/useInvestigations";
import { useRealtime } from "../../shared/realtime";
import { useRealtimeSync } from "../../hooks/useRealtimeSync";
import { Button } from "../../components/common/Button";
import { Badge } from "../../components/common/Badge";
import { LoadingSkeleton } from "../../components/common/LoadingSkeleton";
import { ErrorState } from "../../components/common/ErrorState";
import { ArrowLeft, ExternalLink } from "lucide-react";
import {
  SummaryCard,
  Timeline,
  EvidenceSection,
  GraphIntelligencePreview,
  MemoryContextCard,
  ConsensusCard,
  ExplainabilityAndRecs,
  AgentActivityTable
} from "../../components/investigations/WorkspaceComponents";

export default function InvestigationDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  // 1. Initialize Realtime Stream
  const { isConnected } = useRealtime(id || '');

  // 2. Synchronize Stream to TanStack Query Cache
  useRealtimeSync(id || '');

  // 3. Fetch Investigation Data (Polling disabled if streaming is connected)
  const { data, isLoading, isError, refetch } = useInvestigation(id || '', isConnected);

  if (isLoading) {
    return (
      <div className="space-y-6 pb-12">
        <LoadingSkeleton className="h-24 w-full" />
        <LoadingSkeleton className="h-64 w-full" />
        <div className="grid grid-cols-2 gap-6">
          <LoadingSkeleton className="h-96 w-full" />
          <LoadingSkeleton className="h-96 w-full" />
        </div>
      </div>
    );
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load investigation workspace" onRetry={() => refetch()} />;
  }

  return (
    <div className="space-y-8 pb-12">
      {/* SECTION 1: Header */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 border-b border-border pb-6">
        <div>
          <button
            onClick={() => navigate("/investigations")}
            className="flex items-center text-sm font-medium text-muted hover:text-slate-900 transition-colors mb-4"
          >
            <ArrowLeft className="mr-1 h-4 w-4" /> Back to Investigations
          </button>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold text-slate-900">{data.id}</h1>
            <Badge variant={data.status === 'completed' ? 'success' : 'warning'} className="uppercase">
              {data.status.replace("_", " ")}
            </Badge>
          </div>
          <h2 className="text-xl text-slate-700 font-medium">{data.name}</h2>

          <div className="flex flex-wrap items-center gap-4 mt-4 text-sm text-slate-600">
            <div className="flex items-center gap-1">
              <span className="font-semibold text-slate-900">Marketplace:</span> {data.marketplace}
            </div>
            <div className="flex items-center gap-1">
              <span className="font-semibold text-slate-900">Type:</span> {data.investigationType}
            </div>
            <div className="flex items-center gap-1">
              <span className="font-semibold text-slate-900">Priority:</span>
              <Badge variant={data.plannerPriority === 'critical' ? 'danger' : 'default'} className="uppercase text-[10px] px-1.5 py-0 rounded">
                {data.plannerPriority}
              </Badge>
            </div>
            <div className="flex items-center gap-1">
              <span className="font-semibold text-slate-900">Created:</span> {new Date(data.createdAt).toLocaleString()}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">Export Report</Button>
          <Button>
            View Listing <ExternalLink className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid gap-8">
        {/* SECTION 2: Summary */}
        <section>
          <SummaryCard data={data} />
        </section>

        {/* SECTION 3 & 4: Timeline and Evidence */}
        <section className="grid gap-8 lg:grid-cols-3">
          <div className="lg:col-span-1">
            <Timeline events={data.timeline} />
          </div>
          <div className="lg:col-span-2">
            <EvidenceSection evidence={data.evidence} />
          </div>
        </section>

        {/* SECTION 5 & 6: Graph and Memory Context */}
        <section className="grid gap-8 lg:grid-cols-2">
          <GraphIntelligencePreview id={data.id} />
          <MemoryContextCard memory={data.memoryContext} />
        </section>

        {/* SECTION 7: Consensus */}
        <section>
          <ConsensusCard consensus={data.consensus} />
        </section>

        {/* SECTION 8 & 9: Explainability & Recommendations */}
        <section>
          <ExplainabilityAndRecs id={data.id} fallbackData={data} />
        </section>

        {/* SECTION 10: Agent Activity */}
        <section>
          <AgentActivityTable activities={data.agentActivity} />
        </section>
      </div>
    </div>
  );
}

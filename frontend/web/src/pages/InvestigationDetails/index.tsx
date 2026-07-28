import { useParams, useNavigate } from "react-router-dom";
import { useInvestigationDetails } from "../../hooks/useInvestigations";
import {
  SummaryCard,
  VerifiedRecommendationsSection,
  ProductComparisonMatrix,
  Timeline,
  EvidenceSection,
  GraphIntelligencePreview,
  MemoryContextCard,
  ConsensusCard,
  ExplainabilityAndRecs,
  AgentActivityTable,
  ProviderHealthWidget
} from "../../components/investigations/WorkspaceComponents";
import { Button } from "../../components/common/Button";
import { Badge } from "../../components/common/Badge";
import { ArrowLeft, ExternalLink, RefreshCw, AlertCircle } from "lucide-react";

export function InvestigationDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data, isLoading, isError, error, refetch } = useInvestigationDetails(id || "");

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="text-sm font-medium text-muted">Retrieving Cyber-Intelligence Report...</p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-center">
        <AlertCircle className="h-12 w-12 text-danger" />
        <h2 className="text-xl font-bold text-slate-900">Failed to Load Investigation Report</h2>
        <p className="text-sm text-muted max-w-md">
          {error?.message || "Investigation details could not be retrieved from the server."}
        </p>
        <div className="flex gap-3 pt-2">
          <Button variant="outline" onClick={() => navigate("/investigations")}>
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Workspace
          </Button>
          <Button onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" /> Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* HEADER SECTION */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={() => navigate("/investigations")}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-2xl font-bold tracking-tight text-slate-900">
              {data.name}
            </h1>
            <Badge variant="outline" className="font-mono text-xs">
              ID: {data.id.substring(0, 8)}...
            </Badge>
          </div>
          <div className="flex flex-wrap items-center gap-4 text-xs text-muted pl-11">
            <div className="flex items-center gap-1">
              <span className="font-semibold text-slate-900">Marketplace:</span> {data.marketplace}
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
          <Button variant="outline" onClick={() => window.print()}>Export Report</Button>
          <Button onClick={() => window.open(data.listing_url || "#", "_blank")}>
            View Listing <ExternalLink className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </div>

      <div className="grid gap-8">
        {/* SECTION 1: Provider Health SLA Dashboard */}
        <section>
          <ProviderHealthWidget />
        </section>

        {/* SECTION 2: Summary */}
        <section>
          <SummaryCard data={data} />
        </section>

        {/* SECTION 2.1: Verified Purchase Recommendations & Price Intelligence */}
        <section>
          <VerifiedRecommendationsSection
            products={data.recommendedProducts}
            priceIntel={data.priceIntelligence}
            summary={data.recommendationSummary}
          />
        </section>

        {/* SECTION 2.2: Product Comparison Matrix */}
        {data.productComparison && (
          <section>
            <ProductComparisonMatrix comparison={data.productComparison} />
          </section>
        )}

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

        {/* SECTION 10: Agent Activity Log */}
        <section>
          <AgentActivityTable activities={data.agentActivity} />
        </section>
      </div>
    </div>
  );
}

export default InvestigationDetailsPage;

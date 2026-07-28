import { useState } from "react";
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
  ProviderHealthWidget,
  RiskContributionWidget,
  InvestigationInsightsCard
} from "../../components/investigations/WorkspaceComponents";
import { ReplayModal } from "../../components/investigations/ReplayModal";
import { AskCounterGuardWidget } from "../../components/investigations/AskCounterGuardWidget";
import { ReportExportService } from "../../services/report_export_service";
import { Button } from "../../components/common/Button";
import { Badge } from "../../components/common/Badge";
import { ArrowLeft, ExternalLink, RefreshCw, AlertCircle, ShieldAlert, Play, Clock, Hash, Tag, Store, FileText } from "lucide-react";

export function InvestigationDetailsPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isReplayOpen, setIsReplayOpen] = useState(false);

  const { data, isLoading, isError, error, refetch } = useInvestigationDetails(id || "");

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="text-sm font-medium text-muted">Retrieving Cyber-Intelligence Case Report...</p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4 text-center">
        <AlertCircle className="h-12 w-12 text-danger" />
        <h2 className="text-xl font-bold text-slate-900">Failed to Load Investigation Case Report</h2>
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

  const isHighRisk = data.riskScore > 50;
  const titleDisplay = data.displayTitle || data.name || "Target Assessment";

  return (
    <div className="space-y-8 pb-12">
      {/* Replay Modal Component */}
      <ReplayModal
        isOpen={isReplayOpen}
        onClose={() => setIsReplayOpen(false)}
        agentActivity={data.agentActivity}
        investigationName={titleDisplay}
        riskScore={data.riskScore}
      />

      {/* CYBER INTELLIGENCE CASE HEADER */}
      <div className="rounded-2xl border border-border bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 p-6 text-white shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-3">
            {/* Top Meta Line */}
            <div className="flex items-center gap-3 text-xs">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/investigations")}
                className="text-slate-300 hover:text-white hover:bg-slate-800 p-1.5"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>

              <span className="px-2.5 py-1 rounded-md font-mono font-bold bg-primary/20 text-primary-light border border-primary/40 flex items-center gap-1">
                <Hash className="h-3 w-3" /> CASE-{data.id.substring(0, 8).toUpperCase()}
              </span>

              <Badge variant="outline" className="text-slate-300 border-slate-700 bg-slate-800/80 uppercase font-mono text-[10px]">
                {data.investigationType || "Counterfeit Detection"}
              </Badge>

              <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                data.status === 'completed' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
              }`}>
                {data.status}
              </span>
            </div>

            {/* Case Title */}
            <div className="flex items-center gap-3 pt-1">
              <div className="h-10 w-10 rounded-xl bg-primary/30 border border-primary/50 flex items-center justify-center text-primary-light shrink-0">
                <ShieldAlert className="h-6 w-6" />
              </div>
              <div>
                <h1 className="text-2xl font-black tracking-tight text-white">
                  {titleDisplay}
                </h1>
                <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300 mt-1">
                  <span className="flex items-center gap-1"><Store className="h-3.5 w-3.5 text-slate-400" /> Marketplace: <strong className="text-white">{data.marketplace}</strong></span>
                  <span className="flex items-center gap-1"><Tag className="h-3.5 w-3.5 text-slate-400" /> Priority: <strong className="text-white uppercase">{data.plannerPriority}</strong></span>
                  <span className="flex items-center gap-1"><Clock className="h-3.5 w-3.5 text-slate-400" /> Opened: <strong className="text-white">{new Date(data.createdAt).toLocaleString()}</strong></span>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons & Risk Metric Pill */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0 pt-2 lg:pt-0">
            <div className="p-3 rounded-xl bg-slate-800/90 border border-slate-700 flex items-center gap-3">
              <div className={`h-3 w-3 rounded-full ${isHighRisk ? 'bg-red-500 animate-pulse' : 'bg-emerald-400'}`} />
              <div className="text-right">
                <p className="text-[10px] font-mono uppercase text-slate-400">Risk Score</p>
                <p className={`text-xl font-black font-mono ${isHighRisk ? 'text-red-400' : 'text-emerald-400'}`}>
                  {data.riskScore}/100
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2">
              <Button
                variant="outline"
                className="border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:text-white"
                onClick={() => setIsReplayOpen(true)}
              >
                <Play className="mr-1.5 h-4 w-4 text-primary-light" /> Replay Swarm
              </Button>
              <Button
                variant="outline"
                className="border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700 hover:text-white"
                onClick={() => ReportExportService.generatePrintableReport(data)}
              >
                <FileText className="mr-1.5 h-4 w-4" /> Export Report
              </Button>
              {data.listing_url && (
                <Button className="bg-primary hover:bg-primary-dark text-white font-bold" onClick={() => window.open(data.listing_url, "_blank")}>
                  View Target <ExternalLink className="ml-1.5 h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
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

        {/* SECTION 2.1: Risk Attribution & Insights */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RiskContributionWidget riskScore={data.riskScore} />
          <InvestigationInsightsCard data={data} />
        </section>

        {/* SECTION 2.5: Ask CounterGuard Grounded Assistant */}
        <section>
          <AskCounterGuardWidget investigationId={data.id} />
        </section>

        {/* SECTION 3: Verified Recommended Genuine Options */}
        <section>
          <VerifiedRecommendationsSection products={data.recommendedProducts} />
        </section>

        {/* SECTION 4: Product Comparison Matrix */}
        <section>
          <ProductComparisonMatrix comparison={data.productComparison} />
        </section>

        {/* SECTION 5: Graph Intelligence Preview */}
        <section>
          <GraphIntelligencePreview investigationId={data.id} />
        </section>

        {/* SECTION 6: Consensus & Memory Context */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ConsensusCard consensus={data.consensus} />
          <MemoryContextCard memory={data.memoryContext} />
        </section>

        {/* SECTION 7: Explainability & Recommendations */}
        <section>
          <ExplainabilityAndRecs data={data} />
        </section>

        {/* SECTION 8: Timeline */}
        <section>
          <Timeline events={data.timeline} />
        </section>

        {/* SECTION 9: Evidence Details */}
        <section>
          <EvidenceSection items={data.evidence} />
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

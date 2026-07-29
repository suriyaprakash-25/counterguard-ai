import { useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "../../components/common/PageHeader";
import { Button } from "../../components/common/Button";
import { RefreshCw, ShieldAlert, Activity } from "lucide-react";
import { MetricCardsWidget } from "../../components/dashboard/MetricCardsWidget";
import { InvestigationListWidget } from "../../components/dashboard/InvestigationListWidget";
import { SystemHealthWidget } from "../../components/dashboard/SystemHealthWidget";
import { MarketplaceRiskOverviewWidget } from "../../components/dashboard/MarketplaceRiskOverviewWidget";
import { RiskDistributionWidget } from "../../components/dashboard/RiskDistributionWidget";
import { TopSuspiciousSellersWidget } from "../../components/dashboard/TopSuspiciousSellersWidget";
import { SwarmActivityWidget } from "../../components/dashboard/SwarmActivityWidget";
import { AgentStatsWidget } from "../../components/dashboard/AgentStatsWidget";
import { RiskTrendWidget } from "../../components/dashboard/RiskTrendWidget";

export default function Dashboard() {
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["investigations"] });
    queryClient.invalidateQueries({ queryKey: ["alerts"] });
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <PageHeader
        title="Cyber Intelligence Operations Center"
        description="Autonomous Multi-Agent Counterfeit Intelligence Platform • Real-time Swarm Telemetry & Threat Matrix."
      >
        <Button variant="outline" size="sm" onClick={handleRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Operations
        </Button>
      </PageHeader>

      <div className="flex flex-col gap-6">
        {/* ================================================== */}
        {/* 1. TOP SECTION: 5 KPI CARDS                        */}
        {/* ================================================== */}
        <section>
          <MetricCardsWidget />
        </section>

        {/* ================================================== */}
        {/* 2. SECOND SECTION: RECENT INVESTIGATIONS & HEALTH   */}
        {/* ================================================== */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <InvestigationListWidget />
          </div>
          <div className="lg:col-span-1">
            <SystemHealthWidget />
          </div>
        </section>

        {/* ================================================== */}
        {/* 3. THIRD SECTION: MARKETPLACE RISK & LEADERBOARD   */}
        {/* ================================================== */}
        <section className="space-y-6">
          <MarketplaceRiskOverviewWidget />

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <RiskDistributionWidget />
            <TopSuspiciousSellersWidget />
          </div>
        </section>

        {/* ================================================== */}
        {/* 4. FOURTH SECTION: AI SWARM TELEMETRY & STATS     */}
        {/* ================================================== */}
        <section className="space-y-6">
          <SwarmActivityWidget />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <AgentStatsWidget />
            </div>
            <div className="lg:col-span-1">
              <RiskTrendWidget />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

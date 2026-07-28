import { useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "../../components/common/PageHeader";
import { Button } from "../../components/common/Button";
import { RefreshCw } from "lucide-react";
import { MetricCardsWidget } from "../../components/dashboard/MetricCardsWidget";
import { InvestigationListWidget } from "../../components/dashboard/InvestigationListWidget";
import { AlertListWidget } from "../../components/dashboard/AlertListWidget";
import { MarketplaceActivityWidget } from "../../components/dashboard/MarketplaceActivityWidget";
import { RiskTrendWidget } from "../../components/dashboard/RiskTrendWidget";
import { MiniGraphPreviewWidget } from "../../components/dashboard/MiniGraphPreviewWidget";
import { SystemHealthWidget } from "../../components/dashboard/SystemHealthWidget";

export default function Dashboard() {
  const queryClient = useQueryClient();

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["investigations"] });
    queryClient.invalidateQueries({ queryKey: ["alerts"] });
  };

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="CounterGuard Dashboard"
        description="Autonomous Investigation & Intelligence Overview"
      >
        <Button variant="outline" size="sm" onClick={handleRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </PageHeader>

      <div className="flex flex-col gap-6">
        {/* Section 2: Summary KPI Cards */}
        <section>
          <MetricCardsWidget />
        </section>

        {/* Section 3 & 4: Investigations and Alerts */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <InvestigationListWidget />
          </div>
          <div className="lg:col-span-1">
            <AlertListWidget />
          </div>
        </section>

        {/* Section 5 & 6: Marketplace Activity and Risk Trends */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <MarketplaceActivityWidget />
          <RiskTrendWidget />
        </section>

        {/* Section 7 & 8: Fraud Network Preview and System Health */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <MiniGraphPreviewWidget />
          </div>
          <div className="lg:col-span-1">
            <SystemHealthWidget />
          </div>
        </section>
      </div>
    </div>
  );
}

import { PageHeader } from "../../components/common/PageHeader";
import { DataToolbar } from "../../components/common/DataToolbar";
import {
  InvestigationsTrendChart,
  MarketplaceDistributionChart,
  AgentUtilizationChart
} from "./widgets/Widgets";

export default function AnalyticsCenter() {
  return (
    <div className="flex flex-col h-full pb-4">
      <div className="shrink-0 mb-6">
        <PageHeader
          title="Executive Analytics"
          description="High-level insights into CounterGuard platform performance and investigation trends."
        />
        <div className="mt-4">
          <DataToolbar
            onDateRange={() => {}}
            onFilter={() => {}}
            onRefresh={() => {}}
            onExport={() => {}}
          />
        </div>
      </div>

      <div className="flex-1 space-y-6">
        <InvestigationsTrendChart />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MarketplaceDistributionChart />
          <AgentUtilizationChart />
        </div>
      </div>
    </div>
  );
}

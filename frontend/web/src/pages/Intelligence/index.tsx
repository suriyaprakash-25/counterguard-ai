import { PageHeader } from "../../components/common/PageHeader";
import { Button } from "../../components/common/Button";
import { RefreshCw, Search } from "lucide-react";
import {
  GlobalSummaryWidget, KnownSellersWidget, FraudRingsWidget,
  KnownPatternsWidget, RepeatedImagesWidget, RepeatedPhonesInvoicesWidget,
  SemanticMemoryWidget, GraphStatsWidget
} from "./widgets/Widgets";

export default function IntelligenceCenter() {
  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="space-y-8 pb-12">
      {/* SECTION 1: Header & Search */}
      <PageHeader
        title="Intelligence Center"
        description="Explore accumulated organizational memory and network insights."
      >
        <Button variant="outline" size="sm" onClick={handleRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Data
        </Button>
      </PageHeader>

      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted" />
        <input
          type="text"
          placeholder="Search for Seller, Phone, Invoice, Image, Pattern, Brand..."
          className="w-full h-12 pl-10 pr-4 rounded-lg border border-border bg-surface text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent shadow-sm"
        />
      </div>

      <div className="flex flex-col gap-8">
        <GlobalSummaryWidget />
        <KnownSellersWidget />
        <FraudRingsWidget />
        <KnownPatternsWidget />
        <RepeatedImagesWidget />
        <RepeatedPhonesInvoicesWidget />
        <SemanticMemoryWidget />
        <GraphStatsWidget />
      </div>
    </div>
  );
}

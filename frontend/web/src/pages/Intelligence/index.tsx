import React, { useState } from "react";
import { PageHeader } from "../../components/common/PageHeader";
import { Button } from "../../components/common/Button";
import { RefreshCw, Search, ShieldAlert, Network, Sparkles, Database, BarChart3 } from "lucide-react";
import { ThreatOverviewHeader } from "./components/ThreatOverviewHeader";
import { HighRiskSellersWidget } from "./components/HighRiskSellersWidget";
import { TrendingProductsWidget } from "./components/TrendingProductsWidget";
import { IntelligenceLifecycleDashboard } from "./components/IntelligenceLifecycleDashboard";
import {
  GlobalSummaryWidget, KnownSellersWidget, FraudRingsWidget,
  KnownPatternsWidget, RepeatedImagesWidget, RepeatedPhonesInvoicesWidget,
  SemanticMemoryWidget, GraphStatsWidget
} from "./widgets/Widgets";

export default function IntelligenceCenter() {
  const [search, setSearch] = useState("");

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <div className="space-y-6 pb-16 text-slate-900 dark:text-slate-100">
      {/* Page Header */}
      <PageHeader
        title="Executive Threat Intelligence Command Center"
        description="Global threat matrix, multi-marketplace fraud ring telemetry, and live merchant directory"
      >
        <Button variant="outline" size="sm" onClick={handleRefresh}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Live Data
        </Button>
      </PageHeader>

      {/* Autonomous Closed-Loop Intelligence Lifecycle Dashboard */}
      <IntelligenceLifecycleDashboard />

      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search Threat Intelligence by Seller, Phone, GST, Fraud Ring, Brand, or Evidence..."
          className="w-full h-11 pl-10 pr-4 rounded-xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-sm outline-none focus:border-violet-500 focus:ring-1 focus:ring-violet-500 transition-all shadow-sm"
        />
      </div>

      {/* PHASE 1 — Executive Threat Overview KPI Banner */}
      <ThreatOverviewHeader
        threatIndex={78}
        activeRingsCount={2}
        highRiskSellersCount={8}
        takedownsCount={14}
      />

      {/* Split Grid: High Risk Sellers & Trending Products */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HighRiskSellersWidget />
        <TrendingProductsWidget />
      </div>

      {/* Intelligence Core Widgets */}
      <div className="space-y-6 pt-4 border-t border-slate-200 dark:border-slate-800">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-2">
          <Database className="h-4 w-4 text-violet-500" /> Organizational Threat Memory & Fraud Ring Registry
        </h3>
        <GlobalSummaryWidget />
        <FraudRingsWidget />
        <KnownSellersWidget />
        <KnownPatternsWidget />
        <RepeatedImagesWidget />
        <RepeatedPhonesInvoicesWidget />
        <SemanticMemoryWidget />
        <GraphStatsWidget />
      </div>
    </div>
  );
}

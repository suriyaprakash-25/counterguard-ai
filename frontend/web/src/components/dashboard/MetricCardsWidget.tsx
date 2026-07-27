import { Activity, ShieldAlert, AlertTriangle, Network } from "lucide-react";
import { useDashboardSummary } from "../../hooks/useDashboard";
import { MetricCard } from "./MetricCard";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";

export function MetricCardsWidget() {
  const { data, isLoading, isError, refetch } = useDashboardSummary();

  if (isLoading) {
    return (
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {[1, 2, 3, 4].map((i) => (
          <LoadingSkeleton key={i} className="h-32 w-full" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load dashboard metrics" onRetry={() => refetch()} />;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
      <MetricCard
        title="Active Investigations"
        value={data.activeInvestigations}
        icon={Activity}
        trend={data.investigationTrend}
        description="vs last week"
      />
      <MetricCard
        title="Active Alerts"
        value={data.activeAlerts}
        icon={AlertTriangle}
        trend={data.alertTrend}
        description="vs last week"
      />
      <MetricCard
        title="High-Risk Sellers"
        value={data.highRiskSellers}
        icon={ShieldAlert}
        trend={data.sellerTrend}
        description="vs last week"
      />
      <MetricCard
        title="Fraud Rings Detected"
        value={data.fraudRingsDetected}
        icon={Network}
        trend={data.ringTrend}
        description="vs last week"
      />
    </div>
  );
}

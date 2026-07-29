import { useNavigate } from "react-router-dom";
import { Activity, ShieldAlert, AlertTriangle, Network, Layers } from "lucide-react";
import { useDashboardSummary } from "../../hooks/useDashboard";
import { MetricCard } from "./MetricCard";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";

export function MetricCardsWidget() {
  const { data, isLoading, isError, refetch } = useDashboardSummary();
  const navigate = useNavigate();

  if (isLoading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {[1, 2, 3, 4, 5].map((i) => (
          <LoadingSkeleton key={i} className="h-36 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load dashboard metrics" onRetry={() => refetch()} />;
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
      {/* CARD 1: Total Investigations */}
      <MetricCard
        title="Total Investigations"
        value={data.totalInvestigations || 154}
        icon={Layers}
        trend={data.totalTrend || 14}
        description="vs last month"
        breakdown={[
          { label: "Done", value: data.completedInvestigations || 126, color: "text-emerald-600" },
          { label: "Run", value: data.runningInvestigations || 18, color: "text-amber-600" },
          { label: "Fail", value: data.failedInvestigations || 10, color: "text-red-500" }
        ]}
        sparklineData={[90, 105, 120, 110, 135, 142, 154]}
        iconBgClass="bg-blue-500/10"
        iconColorClass="text-blue-600"
        tooltip="Total multi-agent investigations executed across all platforms."
        onClick={() => navigate("/investigations")}
      />

      {/* CARD 2: Active Investigations */}
      <MetricCard
        title="Active Investigations"
        value={data.activeInvestigations || 18}
        icon={Activity}
        trend={data.investigationTrend || 4}
        description="swarms running"
        sparklineData={[8, 12, 10, 15, 14, 16, 18]}
        iconBgClass="bg-amber-500/10"
        iconColorClass="text-amber-600"
        tooltip="Active LangGraph multi-agent swarms currently executing."
        onClick={() => navigate("/investigations")}
      />

      {/* CARD 3: Active Alerts */}
      <MetricCard
        title="Active Security Alerts"
        value={data.activeAlerts || 3}
        icon={AlertTriangle}
        trend={data.alertTrend || -8}
        description="vs last week"
        sparklineData={[8, 6, 9, 5, 4, 3, 3]}
        iconBgClass="bg-red-500/10"
        iconColorClass="text-red-600"
        tooltip="Unresolved risk anomalies and marketplace security alerts."
        onClick={() => navigate("/alerts")}
      />

      {/* CARD 4: High-Risk Sellers */}
      <MetricCard
        title="High-Risk Sellers"
        value={data.highRiskSellers || 12}
        icon={ShieldAlert}
        trend={data.sellerTrend || 15}
        description="entities flagged"
        sparklineData={[4, 6, 8, 7, 10, 11, 12]}
        iconBgClass="bg-purple-500/10"
        iconColorClass="text-purple-600"
        tooltip="Sellers with average risk scores exceeding 60."
        onClick={() => navigate("/threats")}
      />

      {/* CARD 5: Fraud Rings Detected */}
      <MetricCard
        title="Fraud Rings Detected"
        value={data.fraudRingsDetected || 4}
        icon={Network}
        trend={data.ringTrend || 2}
        description="sybil clusters"
        sparklineData={[1, 1, 2, 2, 3, 3, 4]}
        iconBgClass="bg-emerald-500/10"
        iconColorClass="text-emerald-600"
        tooltip="GraphRAG identified seller collusion clusters."
        onClick={() => navigate("/graph")}
      />
    </div>
  );
}

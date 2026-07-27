import { useNavigate } from "react-router-dom";
import { useRecentAlerts } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Badge } from "../common/Badge";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { EmptyState } from "../common/EmptyState";
import { BellRing, ChevronRight } from "lucide-react";
import type { AlertSummary } from "../../types/dashboard";

function AlertRow({ alert, onClick }: { alert: AlertSummary; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className="flex items-start gap-4 rounded-lg border border-border p-4 transition-colors hover:bg-slate-50 cursor-pointer"
    >
      <div className="mt-1">
        <Badge
          variant={
            alert.severity === "critical"
              ? "danger"
              : alert.severity === "high"
              ? "warning"
              : alert.severity === "medium"
              ? "default"
              : "outline"
          }
        >
          {alert.severity.toUpperCase()}
        </Badge>
      </div>
      <div className="flex-1 space-y-1">
        <h4 className="text-sm font-semibold text-slate-900">{alert.title}</h4>
        <p className="text-sm text-muted">{alert.reason}</p>
        <p className="text-xs text-muted mt-2">
          {new Date(alert.timestamp).toLocaleString()}
        </p>
      </div>
      <ChevronRight className="h-5 w-5 text-slate-300 self-center" />
    </div>
  );
}

export function AlertListWidget() {
  const { data, isLoading, isError, refetch } = useRecentAlerts();
  const navigate = useNavigate();

  if (isLoading) {
    return <LoadingSkeleton className="h-[400px] w-full" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load alerts" onRetry={() => refetch()} />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Alerts</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyState
            icon={BellRing}
            title="No New Alerts"
            description="Your environment is secure and there are no active alerts."
          />
        ) : (
          <div className="space-y-3">
            {data.map((alert) => (
              <AlertRow key={alert.id} alert={alert} onClick={() => navigate("/alerts")} />
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

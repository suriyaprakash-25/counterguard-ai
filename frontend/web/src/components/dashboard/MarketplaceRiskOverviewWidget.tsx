import { useMarketplaceMetrics } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { ShoppingBag, TrendingUp, ShieldAlert } from "lucide-react";

export function MarketplaceRiskOverviewWidget() {
  const { data, isLoading, isError, refetch } = useMarketplaceMetrics();

  if (isLoading) {
    return <LoadingSkeleton className="h-[260px] w-full rounded-xl" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load marketplace risk metrics" onRetry={() => refetch()} />;
  }

  return (
    <Card className="shadow-sm border-border">
      <CardHeader className="pb-3 border-b border-border/60">
        <CardTitle className="flex items-center gap-2 text-base font-bold text-slate-900">
          <ShoppingBag className="h-5 w-5 text-primary" />
          Marketplace Threat & Risk Matrix
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          {data.map((m) => {
            const isHigh = m.averageRisk > 50;
            return (
              <div
                key={m.name}
                className="p-4 rounded-xl border border-border bg-slate-50/50 hover:bg-white hover:shadow-sm transition-all duration-200"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-sm text-slate-900">{m.name}</span>
                  <span className="text-[10px] font-mono font-bold px-1.5 py-0.5 rounded bg-slate-200 text-slate-700">
                    {m.investigations} Cases
                  </span>
                </div>

                <div className="mt-3 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-500 font-medium">Avg Risk Score:</span>
                    <span className={`font-mono font-black ${isHigh ? "text-red-600" : "text-emerald-600"}`}>
                      {m.averageRisk}/100
                    </span>
                  </div>

                  {/* Progress bar */}
                  <div className="h-2 w-full bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${isHigh ? "bg-red-500" : "bg-emerald-500"}`}
                      style={{ width: `${m.averageRisk}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between text-[11px] pt-1 text-slate-500 font-medium">
                    <span>High Risk: <strong className="text-slate-800 font-mono">{m.highRiskCount}</strong></span>
                    <span>Counterfeit: <strong className="text-slate-800 font-mono">{m.counterfeitPercentage}%</strong></span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

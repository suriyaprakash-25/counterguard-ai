import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useMarketplaceMetrics } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";

export function MarketplaceActivityWidget() {
  const { data, isLoading, isError, refetch } = useMarketplaceMetrics();

  if (isLoading) {
    return <LoadingSkeleton className="h-[350px] w-full" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load marketplace activity" onRetry={() => refetch()} />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Marketplace Activity</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748b" }} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748b" }} />
              <Tooltip
                cursor={{ fill: "#f1f5f9" }}
                contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)" }}
              />
              <Bar dataKey="investigations" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

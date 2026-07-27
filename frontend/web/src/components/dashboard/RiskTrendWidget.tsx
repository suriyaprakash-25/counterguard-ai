import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useRiskTrend } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";

export function RiskTrendWidget() {
  const { data, isLoading, isError, refetch } = useRiskTrend();

  if (isLoading) {
    return <LoadingSkeleton className="h-[350px] w-full" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load risk trend" onRetry={() => refetch()} />;
  }

  // Format dates for the X-axis
  const formattedData = data.map(item => ({
    ...item,
    formattedDate: new Date(item.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
  }));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Average Risk Trend</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-[300px] w-full mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={formattedData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="formattedDate" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748b" }} dy={10} minTickGap={30} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "#64748b" }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 1px 2px 0 rgba(0, 0, 0, 0.05)" }}
              />
              <Line type="monotone" dataKey="averageRisk" stroke="#f97316" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: "#f97316", strokeWidth: 0 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

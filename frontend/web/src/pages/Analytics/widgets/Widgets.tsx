import { SectionCard } from "../../../components/common/SectionCard";
import { useAnalytics } from "../hooks/useAnalytics";
import { LoadingSkeleton } from "../../../components/common/LoadingSkeleton";
import { ErrorState } from "../../../components/common/ErrorState";
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from "recharts";

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export function InvestigationsTrendChart() {
  const { data, isLoading, isError } = useAnalytics();

  if (isLoading) return <SectionCard title="Investigations Trend"><LoadingSkeleton className="h-64 w-full" /></SectionCard>;
  if (isError || !data) return <SectionCard title="Investigations Trend"><ErrorState message="Failed to load" /></SectionCard>;

  return (
    <SectionCard title="Investigations Over Time" description="Volume and average risk score of investigations.">
      <div className="h-72 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data.investigationsTrend}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis yAxisId="left" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis yAxisId="right" orientation="right" stroke="#ef4444" fontSize={12} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }} />
            <Area yAxisId="left" type="monotone" dataKey="count" name="Investigations" stroke="#3b82f6" fill="#bfdbfe" />
            <Area yAxisId="right" type="monotone" dataKey="risk" name="Avg Risk" stroke="#ef4444" fill="none" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}

export function MarketplaceDistributionChart() {
  const { data, isLoading, isError } = useAnalytics();

  if (isLoading) return <SectionCard title="Marketplaces"><LoadingSkeleton className="h-64 w-full" /></SectionCard>;
  if (isError || !data) return <SectionCard title="Marketplaces"><ErrorState message="Failed to load" /></SectionCard>;

  return (
    <SectionCard title="Marketplace Distribution" description="Where incidents are occurring.">
      <div className="h-64 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data.marketplaceDistribution}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={80}
              paddingAngle={5}
              dataKey="value"
            >
              {data.marketplaceDistribution.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}

export function AgentUtilizationChart() {
  const { data, isLoading, isError } = useAnalytics();

  if (isLoading) return <SectionCard title="Agent Utilization"><LoadingSkeleton className="h-64 w-full" /></SectionCard>;
  if (isError || !data) return <SectionCard title="Agent Utilization"><ErrorState message="Failed to load" /></SectionCard>;

  return (
    <SectionCard title="Agent Utilization" description="API calls by agent type.">
      <div className="h-64 w-full mt-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data.agentUtilization} layout="vertical" margin={{ left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
            <XAxis type="number" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={11} tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0' }} />
            <Bar dataKey="value" name="Calls" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}

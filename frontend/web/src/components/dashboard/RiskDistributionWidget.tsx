import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { ShieldCheck } from "lucide-react";

const RISK_DISTRIBUTION = [
  { name: "Critical (>80)", value: 8, color: "#dc2626", percentage: 5.2 },
  { name: "High (61-80)", value: 24, color: "#f97316", percentage: 15.6 },
  { name: "Medium (41-60)", value: 48, color: "#f59e0b", percentage: 31.2 },
  { name: "Low (21-40)", value: 54, color: "#3b82f6", percentage: 35.1 },
  { name: "Safe (0-20)", value: 20, color: "#10b981", percentage: 13.0 }
];

export function RiskDistributionWidget() {
  return (
    <Card className="shadow-sm border-border">
      <CardHeader className="pb-3 border-b border-border/60">
        <CardTitle className="flex items-center gap-2 text-base font-bold text-slate-900">
          <ShieldCheck className="h-5 w-5 text-emerald-600" />
          Threat Risk Level Distribution
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        <div className="flex flex-col sm:flex-row items-center gap-6">
          {/* Donut Chart */}
          <div className="h-[200px] w-[200px] shrink-0 relative flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={RISK_DISTRIBUTION}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {RISK_DISTRIBUTION.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: number) => [`${val} Cases`, "Investigations"]}
                  contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0", boxShadow: "0 2px 4px rgba(0,0,0,0.05)" }}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-2xl font-black font-mono text-slate-900">154</span>
              <span className="text-[10px] text-slate-500 font-bold uppercase">Total Cases</span>
            </div>
          </div>

          {/* Legend Items */}
          <div className="flex-1 space-y-2.5 w-full text-xs font-medium">
            {RISK_DISTRIBUTION.map((item) => (
              <div key={item.name} className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-2">
                  <span className="h-3 w-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                  <span className="text-slate-700 font-semibold">{item.name}</span>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="font-bold text-slate-900">{item.value} cases</span>
                  <span className="text-slate-400">({item.percentage}%)</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

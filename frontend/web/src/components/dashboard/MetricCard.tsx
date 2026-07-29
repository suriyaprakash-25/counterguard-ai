import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "../common/Card";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: number;
  description?: string;
  breakdown?: { label: string; value: number; color?: string }[];
  sparklineData?: number[];
  onClick?: () => void;
  tooltip?: string;
  iconBgClass?: string;
  iconColorClass?: string;
}

export function MetricCard({
  title,
  value,
  icon: Icon,
  trend,
  description,
  breakdown,
  sparklineData = [12, 18, 14, 22, 28, 24, 32],
  onClick,
  tooltip,
  iconBgClass = "bg-primary/10",
  iconColorClass = "text-primary"
}: MetricCardProps) {
  const maxSpark = Math.max(...sparklineData, 1);
  const points = sparklineData
    .map((val, idx) => {
      const x = (idx / (sparklineData.length - 1)) * 64;
      const y = 20 - (val / maxSpark) * 16;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <Card
      onClick={onClick}
      title={tooltip}
      className={`transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 ${
        onClick ? "cursor-pointer" : ""
      }`}
    >
      <CardContent className="p-5 flex flex-col justify-between h-full">
        <div>
          {/* Header & Icon */}
          <div className="flex items-center justify-between gap-2">
            <p className="text-xs font-bold text-slate-500 uppercase tracking-wider">{title}</p>
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl shrink-0 ${iconBgClass}`}>
              <Icon className={`h-5 w-5 ${iconColorClass}`} />
            </div>
          </div>

          {/* Main Metric Value & Trend Sparkline */}
          <div className="flex items-baseline justify-between mt-2">
            <div className="text-3xl font-black text-slate-900 tracking-tight">{value}</div>

            {/* Mini SVG Sparkline */}
            <div className="h-6 w-16 opacity-75">
              <svg className="h-full w-full overflow-visible" viewBox="0 0 64 20">
                <polyline
                  fill="none"
                  stroke={trend && trend < 0 ? "#ef4444" : "#10b981"}
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  points={points}
                />
              </svg>
            </div>
          </div>

          {/* Trend Tag & Description */}
          <div className="mt-2 flex items-center gap-1.5 text-xs">
            {trend !== undefined && (
              <span
                className={`px-1.5 py-0.5 rounded font-mono font-bold ${
                  trend >= 0 ? "bg-emerald-50 text-emerald-700 border border-emerald-200" : "bg-red-50 text-red-700 border border-red-200"
                }`}
              >
                {trend > 0 ? "+" : ""}
                {trend}%
              </span>
            )}
            {description && <span className="text-slate-500 font-medium">{description}</span>}
          </div>
        </div>

        {/* Optional Sub-Breakdown Pills */}
        {breakdown && breakdown.length > 0 && (
          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px]">
            {breakdown.map((item, idx) => (
              <div key={idx} className="flex items-center gap-1">
                <span className="text-slate-400">{item.label}:</span>
                <span className={`font-bold font-mono ${item.color || "text-slate-800"}`}>{item.value}</span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

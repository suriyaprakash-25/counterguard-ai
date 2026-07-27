import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "../common/Card";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: number;
  description?: string;
}

export function MetricCard({ title, value, icon: Icon, trend, description }: MetricCardProps) {
  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm font-medium text-muted">{title}</p>
            <div className="text-3xl font-bold text-slate-900">{value}</div>
          </div>
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2 text-sm">
          {trend !== undefined && (
            <span className={`font-medium ${trend >= 0 ? "text-success" : "text-danger"}`}>
              {trend > 0 ? "+" : ""}{trend}%
            </span>
          )}
          {description && <span className="text-muted">{description}</span>}
        </div>
      </CardContent>
    </Card>
  );
}

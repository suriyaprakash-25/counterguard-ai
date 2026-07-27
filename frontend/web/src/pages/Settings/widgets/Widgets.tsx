import { SectionCard } from "../../../components/common/SectionCard";
import { useSettings } from "../hooks/useSettings";
import { LoadingSkeleton } from "../../../components/common/LoadingSkeleton";
import { ErrorState } from "../../../components/common/ErrorState";
import { Button } from "../../../components/common/Button";
import { Badge } from "../../../components/common/Badge";
import { CheckCircle2, AlertTriangle, XCircle, Shield, Database } from "lucide-react";

export function SystemStatusWidget() {
  const { data, isLoading, isError } = useSettings();

  if (isLoading) return <SectionCard title="System Health"><LoadingSkeleton className="h-48 w-full" /></SectionCard>;
  if (isError || !data) return <SectionCard title="System Health"><ErrorState message="Failed to load" /></SectionCard>;

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'operational': return <CheckCircle2 className="h-5 w-5 text-success" />;
      case 'degraded': return <AlertTriangle className="h-5 w-5 text-warning" />;
      case 'offline': return <XCircle className="h-5 w-5 text-danger" />;
      default: return null;
    }
  };

  return (
    <SectionCard title="System Health" description={`CounterGuard Core v${data.version} - Last updated ${new Date(data.lastUpdated).toLocaleString()}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-4">
        {data.systemStatus.map(service => (
          <div key={service.service} className="p-4 rounded-xl border border-border bg-slate-50 flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-900">{service.service}</p>
              <p className="text-xs text-muted mt-1">{service.latency}ms latency</p>
            </div>
            <div className="flex flex-col items-end gap-2">
              {getStatusIcon(service.status)}
              <Badge variant={service.status === 'operational' ? 'success' : 'danger'} className="text-[10px] capitalize">
                {service.status}
              </Badge>
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

export function ConfigurationWidget() {
  return (
    <SectionCard title="Platform Configuration" description="Manage global investigation parameters.">
      <div className="space-y-6 mt-4">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex-1 space-y-4 p-4 rounded-xl border border-border bg-slate-50">
            <div className="flex items-center gap-2 mb-4"><Shield className="h-5 w-5 text-primary"/> <h3 className="font-semibold text-slate-900">Investigation Engine</h3></div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-slate-700">Autonomous Escalation Threshold</label>
              <input type="range" min="0" max="100" defaultValue="85" className="w-full accent-primary" />
              <div className="flex justify-between text-xs text-muted"><span>0 (Manual)</span><span>85 (Current)</span><span>100 (Aggressive)</span></div>
            </div>
          </div>

          <div className="flex-1 space-y-4 p-4 rounded-xl border border-border bg-slate-50">
            <div className="flex items-center gap-2 mb-4"><Database className="h-5 w-5 text-primary"/> <h3 className="font-semibold text-slate-900">Memory & Storage</h3></div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-slate-700">Vector Store Sync</p>
                <p className="text-xs text-muted">ChromaDB refresh interval</p>
              </div>
              <select className="p-2 border border-border rounded-md text-sm bg-white">
                <option>Real-time</option>
                <option>Every 5 minutes</option>
                <option>Hourly</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex justify-end pt-4 border-t border-border">
          <Button variant="default">Save Configuration</Button>
        </div>
      </div>
    </SectionCard>
  );
}

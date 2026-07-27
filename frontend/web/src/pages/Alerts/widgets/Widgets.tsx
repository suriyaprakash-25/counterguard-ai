import { Badge } from "../../../components/common/Badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/common/Table";
import { LoadingSkeleton } from "../../../components/common/LoadingSkeleton";
import { ErrorState } from "../../../components/common/ErrorState";
import { useAlerts, useAlertDetails } from "../hooks/useAlerts";
import { ShieldAlert, AlertTriangle, Info, Bell, CheckCircle2, Search, ExternalLink } from "lucide-react";
import { DataToolbar } from "../../../components/common/DataToolbar";
import { Button } from "../../../components/common/Button";

interface AlertListWidgetProps {
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function AlertListWidget({ selectedId, onSelect }: AlertListWidgetProps) {
  const { data, isLoading, isError, refetch } = useAlerts();

  if (isLoading) return <LoadingSkeleton className="h-full w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load alerts" onRetry={() => refetch()} />;

  const getSeverityIcon = (level: string) => {
    switch(level) {
      case 'critical': return <ShieldAlert className="h-4 w-4 text-danger" />;
      case 'high': return <AlertTriangle className="h-4 w-4 text-warning" />;
      case 'medium': return <Info className="h-4 w-4 text-primary" />;
      default: return <Bell className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-surface">
      <div className="p-4 border-b border-border sticky top-0 bg-surface z-10">
        <DataToolbar
          searchPlaceholder="Search alerts..."
          onSearch={() => {}}
          onFilter={() => {}}
          onRefresh={refetch}
          className="border-none shadow-none bg-transparent p-0"
        />
      </div>
      <div className="flex-1 overflow-y-auto">
        <Table>
          <TableHeader className="sticky top-0 bg-slate-50 shadow-sm z-10">
            <TableRow>
              <TableHead className="w-10"></TableHead>
              <TableHead>Alert</TableHead>
              <TableHead>Marketplace</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Time</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map(alert => (
              <TableRow
                key={alert.id}
                onClick={() => onSelect(alert.id)}
                className={`cursor-pointer transition-colors ${selectedId === alert.id ? 'bg-blue-50/50' : 'hover:bg-slate-50'}`}
              >
                <TableCell>{getSeverityIcon(alert.severity)}</TableCell>
                <TableCell>
                  <p className="font-medium text-slate-900 text-sm line-clamp-1">{alert.title}</p>
                  <p className="text-[10px] text-muted font-mono">{alert.id}</p>
                </TableCell>
                <TableCell className="text-sm">{alert.marketplace}</TableCell>
                <TableCell>
                  <Badge variant={alert.status === 'new' ? 'danger' : alert.status === 'acknowledged' ? 'warning' : 'outline'}>
                    {alert.status}
                  </Badge>
                </TableCell>
                <TableCell className="text-right text-xs text-muted">
                  {new Date(alert.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}

interface AlertDetailsWidgetProps {
  alertId: string | null;
}

export function AlertDetailsWidget({ alertId }: AlertDetailsWidgetProps) {
  const { data, isLoading, isError } = useAlertDetails(alertId);

  if (!alertId) {
    return (
      <div className="h-full flex flex-col items-center justify-center text-center p-8 bg-slate-50 border-dashed">
        <div className="h-16 w-16 rounded-full bg-slate-200 flex items-center justify-center mb-4">
          <Search className="h-8 w-8 text-slate-400" />
        </div>
        <h3 className="text-lg font-medium text-slate-900 mb-2">No Alert Selected</h3>
        <p className="text-sm text-muted">Select an alert from the inbox to view its intelligence and recommended actions.</p>
      </div>
    );
  }

  if (isLoading) return <LoadingSkeleton className="h-full w-full p-6" />;
  if (isError || !data) return <ErrorState message="Failed to load alert details" />;

  return (
    <div className="flex flex-col h-full bg-surface">
      <div className="p-6 border-b border-border bg-slate-50/50">
        <div className="flex justify-between items-start mb-4">
          <Badge variant={data.severity === 'critical' ? 'danger' : data.severity === 'high' ? 'warning' : 'default'} className="uppercase">
            {data.severity} Severity
          </Badge>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">Acknowledge</Button>
            <Button variant="outline" size="sm">Dismiss</Button>
          </div>
        </div>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">{data.title}</h2>
        <div className="flex items-center gap-4 text-sm text-muted">
          <span>{data.type}</span>
          <span>•</span>
          <span>Risk: <span className="font-semibold text-danger">{data.riskScore}</span></span>
          <span>•</span>
          <span>{new Date(data.timestamp).toLocaleString()}</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-8">
        <section>
          <h4 className="text-sm font-semibold text-slate-900 mb-2">Intelligence Summary</h4>
          <p className="text-sm text-slate-700 leading-relaxed p-4 bg-slate-50 rounded-lg border border-border">
            {data.description}
          </p>
        </section>

        <section>
          <h4 className="text-sm font-semibold text-slate-900 mb-3">Related Entities</h4>
          <div className="space-y-2">
            {data.relatedEntities.map(entity => (
              <div key={entity.id} className="flex justify-between items-center p-3 rounded border border-border bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer group">
                <div>
                  <p className="text-sm font-medium text-slate-900 group-hover:text-primary transition-colors">{entity.label}</p>
                  <p className="text-[10px] text-muted uppercase font-mono">{entity.type} - {entity.id}</p>
                </div>
                <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-primary" />
              </div>
            ))}
          </div>
        </section>

        <section>
          <h4 className="text-sm font-semibold text-slate-900 mb-3">Recommended Actions</h4>
          <ul className="space-y-2">
            {data.recommendedActions.map((action, idx) => (
              <li key={idx} className="flex items-center gap-3 p-3 bg-blue-50/50 rounded border border-blue-100">
                <CheckCircle2 className="h-4 w-4 text-primary shrink-0" />
                <span className="text-sm text-slate-800">{action}</span>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}

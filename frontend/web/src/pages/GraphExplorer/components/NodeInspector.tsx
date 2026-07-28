import { Card, CardHeader, CardTitle, CardContent } from "../../../components/common/Card";
import { Badge } from "../../../components/common/Badge";
import { LoadingSkeleton } from "../../../components/common/LoadingSkeleton";
import { useNodeDetails } from "../hooks/useGraph";
import { ExternalLink, ShieldAlert, Link2, Search, Database, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "../../../components/common/Button";

interface NodeInspectorProps {
  nodeId: string | null;
}

export function NodeInspector({ nodeId }: NodeInspectorProps) {
  const { data: details, isLoading, isError, error, refetch } = useNodeDetails(nodeId);

  if (!nodeId) {
    return (
      <Card className="h-full flex flex-col items-center justify-center text-center p-8 bg-slate-50 border-dashed">
        <div className="h-16 w-16 rounded-full bg-slate-200 flex items-center justify-center mb-4">
          <Search className="h-8 w-8 text-slate-400" />
        </div>
        <h3 className="text-lg font-medium text-slate-900 mb-2">No Node Selected</h3>
        <p className="text-sm text-muted">Click on any node in the graph canvas to inspect its details, relationships, and risk factors.</p>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className="h-full">
        <CardHeader><LoadingSkeleton className="h-6 w-32" /></CardHeader>
        <CardContent className="space-y-4">
          <LoadingSkeleton className="h-24 w-full" />
          <LoadingSkeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (isError || !details) {
    return (
      <Card className="h-full flex flex-col items-center justify-center text-center p-6 bg-red-50/40 border-red-200">
        <AlertCircle className="h-10 w-10 text-red-500 mb-2" />
        <h4 className="text-base font-bold text-red-900 mb-1">Failed to Load Node Details</h4>
        <p className="text-xs text-red-700 font-mono mb-3">
          Node ID: '{nodeId}' | Error: {error?.message || "HTTP 404 / Invalid Entity"}
        </p>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-3.5 w-3.5" /> Retry Fetch
        </Button>
      </Card>
    );
  }

  const { node } = details;

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-4 border-b border-border bg-slate-50/50">
        <div className="flex justify-between items-start mb-2">
          <Badge variant="outline" className="uppercase font-mono text-[10px]">{node.type}</Badge>
          {node.riskScore !== undefined && (
            <Badge variant={node.riskScore > 80 ? "danger" : node.riskScore > 50 ? "warning" : "success"}>
              Risk: {node.riskScore}
            </Badge>
          )}
        </div>
        <CardTitle className="text-xl">{node.label}</CardTitle>
        <p className="text-xs text-muted font-mono mt-1">ID: {node.id}</p>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-0">
        <div className="p-6 space-y-6">
          {/* Properties */}
          {node.properties && Object.keys(node.properties).length > 0 && (
            <section>
              <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Properties</h4>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(node.properties).map(([key, value]) => (
                  <div key={key} className="bg-slate-50 p-2 rounded border border-border">
                    <p className="text-[10px] text-slate-500 uppercase">{key}</p>
                    <p className="text-sm font-medium text-slate-900">{String(value)}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Intelligence Snapshot */}
          <section>
            <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Intelligence Snapshot</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center p-2 rounded-lg bg-surface border border-border">
                <span className="text-sm text-slate-600 flex items-center gap-2"><Link2 className="h-4 w-4" /> Degree (Connections)</span>
                <span className="font-semibold text-slate-900">{details.degree}</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-surface border border-border">
                <span className="text-sm text-slate-600 flex items-center gap-2"><ShieldAlert className="h-4 w-4" /> Related Investigations</span>
                <span className="font-semibold text-slate-900">{details.relatedInvestigations}</span>
              </div>
              <div className="flex justify-between items-center p-2 rounded-lg bg-surface border border-border">
                <span className="text-sm text-slate-600 flex items-center gap-2"><Database className="h-4 w-4" /> AI Confidence</span>
                <span className="font-semibold text-slate-900">{details.confidence}%</span>
              </div>
            </div>
          </section>

          {/* Connected Entities */}
          <section>
            <h4 className="text-xs font-semibold text-muted uppercase tracking-wider mb-3">Connected Entities ({details.connectedEntities.length})</h4>
            <div className="space-y-2">
              {details.connectedEntities.map(entity => (
                <div key={entity.id} className="flex items-center justify-between p-3 rounded-lg border border-border bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer group">
                  <div>
                    <p className="text-sm font-medium text-slate-900 group-hover:text-primary transition-colors">{entity.label}</p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-muted uppercase">{entity.type}</span>
                      <span className="text-[10px] text-slate-400">•</span>
                      <span className="text-[10px] font-mono text-slate-500">{entity.relationship}</span>
                    </div>
                  </div>
                  <ExternalLink className="h-4 w-4 text-slate-400 group-hover:text-primary opacity-0 group-hover:opacity-100 transition-all" />
                </div>
              ))}
            </div>
          </section>
        </div>
      </CardContent>
    </Card>
  );
}

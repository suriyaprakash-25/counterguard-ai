import { useFraudNodePreview } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { Network, User, Smartphone, FileText, ShoppingBag } from "lucide-react";

export function MiniGraphPreviewWidget() {
  const { data, isLoading, isError, refetch } = useFraudNodePreview();

  if (isLoading) {
    return <LoadingSkeleton className="h-[350px] w-full" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load graph preview" onRetry={() => refetch()} />;
  }

  const getIcon = (type: string) => {
    switch (type) {
      case "seller": return <User className="h-5 w-5 text-primary" />;
      case "phone": return <Smartphone className="h-5 w-5 text-warning" />;
      case "invoice": return <FileText className="h-5 w-5 text-slate-500" />;
      case "listing": return <ShoppingBag className="h-5 w-5 text-success" />;
      default: return <Network className="h-5 w-5 text-muted" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fraud Network Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="relative flex h-[300px] w-full flex-col items-center justify-center rounded-lg border border-border border-dashed bg-slate-50 p-4 mt-4 overflow-hidden">
          {/* Simulated connections (SVG background) */}
          <svg className="absolute inset-0 h-full w-full opacity-20 pointer-events-none">
            <line x1="50%" y1="20%" x2="20%" y2="50%" stroke="currentColor" strokeWidth="2" />
            <line x1="50%" y1="20%" x2="80%" y2="50%" stroke="currentColor" strokeWidth="2" />
            <line x1="20%" y1="50%" x2="50%" y2="80%" stroke="currentColor" strokeWidth="2" />
            <line x1="80%" y1="50%" x2="50%" y2="80%" stroke="currentColor" strokeWidth="2" />
            <line x1="20%" y1="50%" x2="80%" y2="50%" stroke="currentColor" strokeWidth="2" />
          </svg>

          {/* Simulated nodes */}
          <div className="z-10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full h-full place-items-center">
            {data.slice(0, 5).map((node) => (
              <div
                key={node.id}
                className="flex items-center gap-2 rounded-full border border-border bg-surface px-4 py-2 shadow-sm transition-transform hover:scale-105"
              >
                {getIcon(node.type)}
                <span className="text-sm font-medium text-slate-900">{node.label}</span>
              </div>
            ))}
          </div>

          <div className="absolute bottom-4 text-xs text-muted">
            Interactive Cytoscape visualization arriving in Phase 6.
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

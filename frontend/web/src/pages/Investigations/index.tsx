import { useNavigate } from "react-router-dom";
import { useInvestigations } from "../../hooks/useInvestigations";
import { useState } from "react";
import { PageHeader } from "../../components/common/PageHeader";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/common/Table";
import { Badge } from "../../components/common/Badge";
import { LoadingSkeleton } from "../../components/common/LoadingSkeleton";
import { ErrorState } from "../../components/common/ErrorState";
import { EmptyState } from "../../components/common/EmptyState";
import { Search, Plus, Sparkles } from "lucide-react";
import { Button } from "../../components/common/Button";
import type { InvestigationSummary } from "../../types/investigations";
import { CreateInvestigationDialog } from "./CreateInvestigationDialog";
import { RoleGuard } from "../../features/auth/components/RoleGuard";
import { Scale } from "lucide-react";
import { InvestigationComparisonModal } from "./InvestigationComparisonModal";
import { ProductDiscoveryDrawer } from "../../components/discovery/ProductDiscoveryDrawer";


export default function Investigations() {
  const { data, isLoading, isError, refetch } = useInvestigations(1, {});
  const navigate = useNavigate();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [isDiscoveryOpen, setIsDiscoveryOpen] = useState(false);
  const [discoveryPrefillUrl, setDiscoveryPrefillUrl] = useState('');
  const [discoveryPrefillTitle, setDiscoveryPrefillTitle] = useState('');

  const handleInvestigateCandidate = (url: string, title: string) => {
    setDiscoveryPrefillUrl(url);
    setDiscoveryPrefillTitle(title);
    setIsDialogOpen(true);
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex items-start justify-between">
        <PageHeader
          title="Investigations"
          description="Manage and monitor autonomous investigations across all marketplaces."
        />
        <div className="flex gap-2">
          {data && data.length >= 2 && (
            <Button variant="outline" onClick={() => setIsCompareOpen(true)}>
              <Scale className="mr-2 h-4 w-4" /> Compare Cases
            </Button>
          )}
          <Button
            id="open-product-discovery-btn"
            variant="outline"
            onClick={() => setIsDiscoveryOpen(true)}
            className="border-violet-500/40 text-violet-300 hover:bg-violet-500/10"
          >
            <Sparkles className="mr-2 h-4 w-4" /> Discover Products
          </Button>
          <RoleGuard require="Investigator">
            <Button onClick={() => setIsDialogOpen(true)}>
              <Plus className="mr-2 h-4 w-4" /> New Investigation
            </Button>
          </RoleGuard>
        </div>
      </div>

      <ProductDiscoveryDrawer
        isOpen={isDiscoveryOpen}
        onClose={() => setIsDiscoveryOpen(false)}
        onInvestigateUrl={handleInvestigateCandidate}
      />

      <CreateInvestigationDialog
        isOpen={isDialogOpen}
        onClose={() => { setIsDialogOpen(false); setDiscoveryPrefillUrl(''); setDiscoveryPrefillTitle(''); }}
        initialUrl={discoveryPrefillUrl}
        initialTitle={discoveryPrefillTitle}
      />
      {data && (
        <InvestigationComparisonModal
          isOpen={isCompareOpen}
          onClose={() => setIsCompareOpen(false)}
          investigations={data}
        />
      )}

      <div className="rounded-xl border border-border bg-surface shadow-sm overflow-hidden">
        {isLoading ? (
          <div className="p-6"><LoadingSkeleton className="h-[600px] w-full" /></div>
        ) : isError || !data ? (
          <ErrorState message="Failed to load investigations" onRetry={() => refetch()} />
        ) : data.length === 0 ? (
          <EmptyState
            icon={Search}
            title="No Investigations Found"
            description="There are currently no investigations matching your criteria."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Investigation Name</TableHead>
                <TableHead>Marketplace</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead className="text-right">Last Updated</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((inv: InvestigationSummary) => (
                <TableRow
                  key={inv.id}
                  onClick={() => navigate(`/investigations/${inv.id}`)}
                  className="cursor-pointer hover:bg-slate-50 transition-colors"
                >
                  <TableCell className="font-medium">{inv.id}</TableCell>
                  <TableCell>
                    <div className="flex flex-col">
                      <span className="font-medium text-slate-900">{inv.name}</span>
                      <span className="text-xs text-muted">{inv.investigationType} • {inv.agentCount} Agents</span>
                    </div>
                  </TableCell>
                  <TableCell>{inv.marketplace}</TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        inv.plannerPriority === "critical" ? "danger"
                        : inv.plannerPriority === "high" ? "warning"
                        : "default"
                      }
                    >
                      {inv.plannerPriority.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={
                        inv.status === "completed" ? "success"
                        : inv.status === "failed" ? "danger"
                        : "outline"
                      }
                    >
                      {inv.status.replace("_", " ").toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-16 overflow-hidden rounded-full bg-slate-200">
                        <div
                          className={`h-full ${inv.riskScore > 80 ? "bg-danger" : inv.riskScore > 50 ? "bg-warning" : "bg-success"}`}
                          style={{ width: `${inv.riskScore}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium">{inv.riskScore}</span>
                    </div>
                  </TableCell>
                  <TableCell className="text-muted text-right">
                    {new Date(inv.lastUpdated).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </div>
  );
}

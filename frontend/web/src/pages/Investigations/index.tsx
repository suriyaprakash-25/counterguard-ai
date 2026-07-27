import { useNavigate } from "react-router-dom";
import { useInvestigations } from "../../hooks/useInvestigations";
import { PageHeader } from "../../components/common/PageHeader";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../components/common/Table";
import { Badge } from "../../components/common/Badge";
import { LoadingSkeleton } from "../../components/common/LoadingSkeleton";
import { ErrorState } from "../../components/common/ErrorState";
import { EmptyState } from "../../components/common/EmptyState";
import { Search } from "lucide-react";
import type { InvestigationSummary } from "../../types/investigations";

export default function Investigations() {
  const { data, isLoading, isError, refetch } = useInvestigations();
  const navigate = useNavigate();

  return (
    <div className="space-y-6 pb-12">
      <PageHeader
        title="Investigations"
        description="Manage and monitor autonomous investigations across all marketplaces."
      />

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

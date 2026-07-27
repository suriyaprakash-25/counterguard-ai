import { useNavigate } from "react-router-dom";
import { useRecentInvestigations } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../common/Table";
import { Badge } from "../common/Badge";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { EmptyState } from "../common/EmptyState";
import { Search } from "lucide-react";
import type { InvestigationSummary } from "../../types/dashboard";

function InvestigationRow({ inv, onClick }: { inv: InvestigationSummary; onClick: () => void }) {
  return (
    <TableRow onClick={onClick} className="cursor-pointer group">
      <TableCell className="font-medium">{inv.id}</TableCell>
      <TableCell>{inv.name}</TableCell>
      <TableCell>{inv.marketplace}</TableCell>
      <TableCell>
        <Badge
          variant={
            inv.status === "completed" ? "success" : inv.status === "failed" ? "danger" : "default"
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
        {new Date(inv.createdAt).toLocaleDateString()}
      </TableCell>
    </TableRow>
  );
}

export function InvestigationListWidget() {
  const { data, isLoading, isError, refetch } = useRecentInvestigations();
  const navigate = useNavigate();

  if (isLoading) {
    return <LoadingSkeleton className="h-[400px] w-full" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load investigations" onRetry={() => refetch()} />;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Investigations</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyState
            icon={Search}
            title="No Investigations Found"
            description="There are currently no active or recent investigations."
          />
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Marketplace</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Risk Score</TableHead>
                <TableHead className="text-right">Date</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((inv) => (
                <InvestigationRow
                  key={inv.id}
                  inv={inv}
                  onClick={() => navigate(`/investigations/${inv.id}`)}
                />
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}

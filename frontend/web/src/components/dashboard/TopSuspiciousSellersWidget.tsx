import { useSuspiciousSellers } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../common/Table";
import { Badge } from "../common/Badge";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { Store, TrendingUp, ArrowUpRight } from "lucide-react";

export function TopSuspiciousSellersWidget() {
  const { data, isLoading, isError, refetch } = useSuspiciousSellers();

  if (isLoading) {
    return <LoadingSkeleton className="h-[320px] w-full rounded-xl" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load suspicious sellers" onRetry={() => refetch()} />;
  }

  return (
    <Card className="shadow-sm border-border">
      <CardHeader className="pb-3 border-b border-border/60">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-base font-bold text-slate-900">
            <Store className="h-5 w-5 text-amber-600" />
            Top Suspicious Merchant Leaderboard
          </div>
          <span className="text-xs text-slate-500 font-normal">Updated Live</span>
        </CardTitle>
      </CardHeader>

      <CardContent className="p-0">
        <Table>
          <TableHeader className="bg-slate-50/80">
            <TableRow>
              <TableHead className="w-12 text-center font-mono">#</TableHead>
              <TableHead>Merchant Name</TableHead>
              <TableHead>Platform</TableHead>
              <TableHead className="text-center">Cases</TableHead>
              <TableHead>Avg Risk</TableHead>
              <TableHead className="text-right">Threat Level</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((seller) => (
              <TableRow key={seller.rank} className="hover:bg-slate-50/80 transition-colors">
                <TableCell className="text-center font-mono font-bold text-xs text-slate-500">
                  {seller.rank}
                </TableCell>
                <TableCell className="font-semibold text-slate-900 text-xs font-mono">
                  {seller.name}
                </TableCell>
                <TableCell className="text-xs text-slate-600 font-medium">
                  {seller.marketplace}
                </TableCell>
                <TableCell className="text-center font-mono font-bold text-xs">
                  {seller.investigationsCount}
                </TableCell>
                <TableCell className="font-mono text-xs font-bold text-red-600">
                  {seller.averageRisk}/100
                </TableCell>
                <TableCell className="text-right">
                  <Badge
                    variant={
                      seller.riskLevel === "CRITICAL"
                        ? "danger"
                        : seller.riskLevel === "HIGH"
                        ? "warning"
                        : "default"
                    }
                    className="uppercase font-mono text-[10px]"
                  >
                    {seller.riskLevel}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

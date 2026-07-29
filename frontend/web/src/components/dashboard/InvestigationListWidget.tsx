import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useRecentInvestigations } from "../../hooks/useDashboard";
import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../common/Table";
import { Badge } from "../common/Badge";
import { Button } from "../common/Button";
import { LoadingSkeleton } from "../common/LoadingSkeleton";
import { ErrorState } from "../common/ErrorState";
import { EmptyState } from "../common/EmptyState";
import { Search, Eye, Play, ShieldAlert, Store, Clock, Bot } from "lucide-react";
import type { InvestigationSummary } from "../../types/dashboard";
import { QuickViewModal } from "./QuickViewModal";
import { ReplayModal } from "../investigations/ReplayModal";

function getMarketplaceBadge(marketplace: string) {
  const m = marketplace.toLowerCase();
  if (m.includes("amazon")) return { label: "Amazon", color: "bg-amber-500/10 text-amber-700 border-amber-300" };
  if (m.includes("flipkart")) return { label: "Flipkart", color: "bg-blue-500/10 text-blue-700 border-blue-300" };
  if (m.includes("meesho")) return { label: "Meesho", color: "bg-fuchsia-500/10 text-fuchsia-700 border-fuchsia-300" };
  if (m.includes("tradeindia")) return { label: "TradeIndia", color: "bg-emerald-500/10 text-emerald-700 border-emerald-300" };
  if (m.includes("ajio")) return { label: "AJIO", color: "bg-indigo-500/10 text-indigo-700 border-indigo-300" };
  return { label: marketplace || "Global", color: "bg-slate-500/10 text-slate-700 border-slate-300" };
}

export function InvestigationListWidget() {
  const { data, isLoading, isError, refetch } = useRecentInvestigations();
  const navigate = useNavigate();
  const [selectedQuickView, setSelectedQuickView] = useState<InvestigationSummary | null>(null);
  const [selectedReplay, setSelectedReplay] = useState<InvestigationSummary | null>(null);

  if (isLoading) {
    return <LoadingSkeleton className="h-[450px] w-full rounded-xl" />;
  }

  if (isError || !data) {
    return <ErrorState message="Failed to load investigations" onRetry={() => refetch()} />;
  }

  return (
    <>
      {/* Quick View Modal */}
      <QuickViewModal
        isOpen={!!selectedQuickView}
        onClose={() => setSelectedQuickView(null)}
        investigation={selectedQuickView}
        onOpenReplay={() => {
          setSelectedReplay(selectedQuickView);
          setSelectedQuickView(null);
        }}
      />

      {/* Replay Swarm Modal */}
      <ReplayModal
        isOpen={!!selectedReplay}
        onClose={() => setSelectedReplay(null)}
        agentActivity={selectedReplay?.agentActivity || []}
        investigationName={selectedReplay?.name}
        riskScore={selectedReplay?.riskScore}
      />

      <Card className="shadow-sm border-border">
        <CardHeader className="flex flex-row items-center justify-between border-b border-border/60 pb-4">
          <CardTitle className="flex items-center gap-2 text-base font-bold text-slate-900">
            <ShieldAlert className="h-5 w-5 text-primary" />
            Recent Cyber Investigations
          </CardTitle>
          <Button variant="ghost" size="sm" onClick={() => navigate("/investigations")} className="text-xs font-semibold text-primary">
            View All Investigations →
          </Button>
        </CardHeader>

        <CardContent className="p-0 overflow-x-auto">
          {data.length === 0 ? (
            <div className="p-8">
              <EmptyState
                icon={Search}
                title="No Active Investigations Found"
                description="No multi-agent investigations have been logged in the last 30 days."
              />
            </div>
          ) : (
            <Table>
              <TableHeader className="bg-slate-50/80">
                <TableRow>
                  <TableHead className="font-mono text-xs">ID</TableHead>
                  <TableHead>Product Target</TableHead>
                  <TableHead>Marketplace</TableHead>
                  <TableHead>Seller Entity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Risk Score</TableHead>
                  <TableHead>Confidence</TableHead>
                  <TableHead>Agents</TableHead>
                  <TableHead>Execution</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Quick Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((inv) => {
                  const mBadge = getMarketplaceBadge(inv.marketplace);
                  const isHigh = inv.riskScore > 50;

                  return (
                    <TableRow key={inv.id} className="hover:bg-slate-50/80 transition-colors group">
                      {/* ID */}
                      <TableCell
                        className="font-mono font-bold text-xs text-primary cursor-pointer hover:underline"
                        onClick={() => navigate(`/investigations/${inv.id}`)}
                      >
                        #{inv.id.substring(0, 8).toUpperCase()}
                      </TableCell>

                      {/* Product */}
                      <TableCell className="font-semibold text-slate-900 max-w-[200px] truncate" title={inv.product || inv.name}>
                        {inv.product || inv.name}
                      </TableCell>

                      {/* Marketplace Badge */}
                      <TableCell>
                        <span className={`px-2 py-0.5 rounded border text-[11px] font-bold ${mBadge.color}`}>
                          {mBadge.label}
                        </span>
                      </TableCell>

                      {/* Seller */}
                      <TableCell className="text-xs text-slate-600 font-mono max-w-[140px] truncate" title={inv.seller}>
                        {inv.seller || "Verified Store"}
                      </TableCell>

                      {/* Status Badge */}
                      <TableCell>
                        <Badge
                          variant={
                            inv.status === "completed"
                              ? "success"
                              : inv.status === "failed"
                              ? "danger"
                              : "warning"
                          }
                          className="uppercase font-mono text-[10px]"
                        >
                          {inv.status}
                        </Badge>
                      </TableCell>

                      {/* Risk Score Pill */}
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="h-2 w-12 overflow-hidden rounded-full bg-slate-200 shrink-0">
                            <div
                              className={`h-full ${isHigh ? "bg-red-500" : "bg-emerald-500"}`}
                              style={{ width: `${inv.riskScore}%` }}
                            />
                          </div>
                          <span className={`text-xs font-mono font-bold ${isHigh ? "text-red-600" : "text-emerald-600"}`}>
                            {inv.riskScore}/100
                          </span>
                        </div>
                      </TableCell>

                      {/* Confidence */}
                      <TableCell className="font-mono text-xs text-slate-700 font-semibold">
                        {inv.confidence || 76}%
                      </TableCell>

                      {/* Agents Used */}
                      <TableCell>
                        <span className="px-2 py-0.5 rounded bg-slate-100 font-mono text-[10px] font-bold text-slate-700">
                          {inv.agentsUsed || 5} Swarm
                        </span>
                      </TableCell>

                      {/* Execution Time */}
                      <TableCell className="font-mono text-xs text-slate-500">
                        {((inv.executionTimeMs || 35000) / 1000).toFixed(1)}s
                      </TableCell>

                      {/* Created */}
                      <TableCell className="text-xs text-slate-500">
                        {new Date(inv.createdAt).toLocaleDateString()}
                      </TableCell>

                      {/* Quick Actions */}
                      <TableCell className="text-right">
                        <div className="flex items-center justify-end gap-1.5">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Quick View Summary"
                            onClick={() => setSelectedQuickView(inv)}
                            className="h-7 px-2 text-slate-600 hover:text-primary hover:bg-primary/10"
                          >
                            <Eye className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Replay Agent Swarm"
                            onClick={() => setSelectedReplay(inv)}
                            className="h-7 px-2 text-slate-600 hover:text-amber-600 hover:bg-amber-50"
                          >
                            <Play className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </>
  );
}

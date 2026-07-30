/**
 * HistoryTab.tsx — Investigation History Tab (lazy-loaded)
 * Contains: search, filter pills, export/clear actions, history cards.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

import { memo } from "react";
import { Search, History as HistoryIcon, FileDown, Trash2, RotateCcw } from "lucide-react";
import { HistoryTabProps } from "../PopupPage";

export const HistoryTab = memo(function HistoryTab({
  historyList,
  historySearch,
  historyFilter,
  filteredHistory,
  onSearchChange,
  onFilterChange,
  onExportHistory,
  onClearAllHistory,
  onDeleteRecord,
  onOpenDashboardReport,
}: HistoryTabProps) {
  return (
    <div className="p-3.5 space-y-3 animate-fadeInScale">
      {/* ── Search & Filter Toolbar ── */}
      <section
        className="space-y-2 bg-slate-900 p-2.5 rounded-xl border border-slate-800 font-mono text-[10px]"
        aria-label="Search and filter investigation history"
      >
        {/* Search Input */}
        <div className="flex items-center gap-2 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
          <Search className="h-3.5 w-3.5 text-slate-400 shrink-0" aria-hidden="true" />
          <label htmlFor="history-search" className="sr-only">
            Search history
          </label>
          <input
            id="history-search"
            type="search"
            placeholder="Search by title, seller, marketplace..."
            value={historySearch}
            onChange={(e) => onSearchChange(e.target.value)}
            className="bg-transparent text-white w-full focus:outline-none placeholder-slate-500 text-[10px]"
            aria-label="Search investigation history"
            autoComplete="off"
          />
          {historySearch && (
            <button
              onClick={() => onSearchChange("")}
              className="text-slate-500 hover:text-white font-bold"
              aria-label="Clear search"
            >
              ×
            </button>
          )}
        </div>

        {/* Filter Pills & Action Bar */}
        <div className="flex items-center justify-between gap-1">
          <div
            className="flex items-center gap-1 overflow-x-auto"
            role="group"
            aria-label="Filter by threat level"
          >
            {(
              [
                { key: "ALL", label: `ALL (${historyList.length})`, activeClass: "bg-purple-600 text-white" },
                { key: "HIGH", label: "RISK", activeClass: "bg-red-600 text-white" },
                { key: "MEDIUM", label: "MEDIUM", activeClass: "bg-amber-600 text-white" },
                { key: "SAFE", label: "SAFE", activeClass: "bg-emerald-600 text-white" },
              ] as const
            ).map(({ key, label, activeClass }) => (
              <button
                key={key}
                onClick={() => onFilterChange(key)}
                aria-pressed={historyFilter === key}
                className={`px-2 py-0.5 rounded font-bold transition-colors shrink-0 ${
                  historyFilter === key
                    ? activeClass
                    : "bg-slate-950 text-slate-400 border border-slate-800"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1 shrink-0" role="group" aria-label="History management actions">
            <button
              onClick={onExportHistory}
              disabled={historyList.length === 0}
              className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-blue-400 disabled:opacity-40 transition-colors"
              title="Export History JSON"
              aria-label="Export investigation history as JSON"
            >
              <FileDown className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={onClearAllHistory}
              disabled={historyList.length === 0}
              className="p-1 rounded bg-slate-800 hover:bg-red-900 text-red-400 disabled:opacity-40 transition-colors"
              title="Clear All History"
              aria-label="Clear all investigation history"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </section>

      {/* ── History Cards ── */}
      {filteredHistory.length === 0 ? (
        <div
          className="p-8 text-center bg-slate-900/50 rounded-xl border border-slate-800 border-dashed space-y-2 animate-fadeIn"
          role="status"
          aria-label="No investigation history records"
        >
          <HistoryIcon className="h-8 w-8 text-slate-600 mx-auto" aria-hidden="true" />
          <p className="text-xs text-slate-400 font-mono">
            {historySearch
              ? "No records match your search."
              : "No stored investigation records found."}
          </p>
          {historySearch && (
            <button
              onClick={() => onSearchChange("")}
              className="text-[10px] text-purple-400 hover:text-purple-300 font-mono"
            >
              Clear search
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-2" role="list" aria-label="Investigation history records">
          {filteredHistory.map((item) => (
            <article
              key={item.id}
              role="listitem"
              className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2 hover:border-slate-700 transition-colors animate-fadeIn"
              aria-label={`Investigation: ${item.productTitle}`}
            >
              {/* Threat badge + timestamp */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 font-mono">
                  <span
                    className={`text-[9px] font-bold px-2 py-0.5 rounded ${
                      item.threatLevel === "CRITICAL" || item.threatLevel === "HIGH"
                        ? "cg-risk-critical"
                        : item.threatLevel === "MEDIUM"
                        ? "cg-risk-medium"
                        : "cg-risk-safe"
                    }`}
                    aria-label={`Threat level: ${item.threatLevel}, risk score: ${item.riskScore}`}
                  >
                    {item.threatLevel} ({item.riskScore})
                  </span>
                  <span className="text-[9px] bg-slate-950 px-1.5 py-0.5 rounded text-purple-300 border border-slate-800 font-bold">
                    {item.marketplace}
                  </span>
                </div>
                <time
                  className="text-[9px] font-mono text-slate-500"
                  dateTime={item.timestamp}
                  aria-label={`Recorded at ${new Date(item.timestamp).toLocaleString()}`}
                >
                  {new Date(item.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </time>
              </div>

              {/* Product & Seller */}
              <div>
                <h3 className="text-xs font-bold text-white truncate max-w-[340px]" title={item.productTitle}>
                  {item.productTitle}
                </h3>
                <p className="text-[10px] font-mono text-slate-400 truncate">
                  Seller: <span className="text-slate-200">{item.sellerName}</span>
                </p>
              </div>

              {/* Footer: ID + actions */}
              <div className="flex items-center justify-between pt-1 border-t border-slate-800 text-[9px] font-mono">
                <span className="text-slate-500 truncate max-w-[170px]" title={item.investigationId}>
                  INV: {item.investigationId}
                </span>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => onOpenDashboardReport(item.investigationId)}
                    className="px-2 py-1 rounded bg-purple-950 hover:bg-purple-900 text-purple-300 border border-purple-800 font-bold flex items-center gap-1 transition-colors"
                    aria-label={`Reopen investigation ${item.investigationId} in dashboard`}
                  >
                    <RotateCcw className="h-2.5 w-2.5" aria-hidden="true" />
                    Reopen
                  </button>
                  <button
                    onClick={() => onDeleteRecord(item.id)}
                    className="p-1 rounded bg-slate-800 hover:bg-red-950 text-slate-400 hover:text-red-400 transition-colors"
                    title="Delete record"
                    aria-label={`Delete investigation record for ${item.productTitle}`}
                  >
                    <Trash2 className="h-3 w-3" aria-hidden="true" />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
});

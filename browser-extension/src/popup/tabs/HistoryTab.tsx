/**
 * HistoryTab.tsx — Investigation History Tab (lazy-loaded)
 * Complete Enterprise UI/UX with Dual Theme Support (Light & Dark Mode)
 */

import { memo } from "react";
import { Search, History as HistoryIcon, FileDown, Trash2, ExternalLink } from "lucide-react";
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
    <div className="p-4 space-y-3.5 animate-fadeInScale">
      {/* ── Search & Filter Toolbar ── */}
      <section
        className="space-y-2.5 bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800 font-mono text-[10px] shadow-sm transition-colors"
        aria-label="Search and filter investigation history"
      >
        {/* Search Input */}
        <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-950 px-3 py-2 rounded-lg border border-slate-200 dark:border-slate-800">
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
            className="bg-transparent text-slate-900 dark:text-white w-full focus:outline-none placeholder-slate-400 text-xs font-sans"
            aria-label="Search investigation history"
            autoComplete="off"
          />
          {historySearch && (
            <button
              onClick={() => onSearchChange("")}
              className="text-slate-400 hover:text-slate-700 dark:hover:text-white font-bold"
              aria-label="Clear search"
            >
              ×
            </button>
          )}
        </div>

        {/* Filter Pills & Action Bar */}
        <div className="flex items-center justify-between gap-2">
          <div
            className="flex items-center gap-1 overflow-x-auto"
            role="group"
            aria-label="Filter by threat level"
          >
            {(
              [
                { key: "ALL", label: `ALL (${historyList.length})`, activeClass: "bg-purple-600 text-white border-purple-500" },
                { key: "HIGH", label: "RISK", activeClass: "bg-red-600 text-white border-red-500" },
                { key: "MEDIUM", label: "MEDIUM", activeClass: "bg-amber-600 text-white border-amber-500" },
                { key: "SAFE", label: "SAFE", activeClass: "bg-emerald-600 text-white border-emerald-500" },
              ] as const
            ).map(({ key, label, activeClass }) => (
              <button
                key={key}
                onClick={() => onFilterChange(key)}
                aria-pressed={historyFilter === key}
                className={`px-2.5 py-1 rounded-md font-bold transition-colors shrink-0 ${
                  historyFilter === key
                    ? activeClass
                    : "bg-slate-100 dark:bg-slate-950 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-800"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1.5 shrink-0" role="group" aria-label="History management actions">
            <button
              onClick={onExportHistory}
              disabled={historyList.length === 0}
              className="p-1.5 rounded-md bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-blue-600 dark:text-blue-400 disabled:opacity-40 transition-colors"
              title="Export History JSON"
              aria-label="Export investigation history as JSON"
            >
              <FileDown className="h-3.5 w-3.5" />
            </button>
            <button
              onClick={onClearAllHistory}
              disabled={historyList.length === 0}
              className="p-1.5 rounded-md bg-slate-100 dark:bg-slate-800 hover:bg-red-100 dark:hover:bg-red-900/60 text-red-600 dark:text-red-400 disabled:opacity-40 transition-colors"
              title="Clear All History"
              aria-label="Clear all investigation history"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </section>

      {/* ── History Items List ── */}
      {filteredHistory.length === 0 ? (
        <div className="text-center py-10 space-y-2 bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm">
          <HistoryIcon className="h-8 w-8 mx-auto text-slate-300 dark:text-slate-700" aria-hidden="true" />
          <p className="text-xs font-semibold text-slate-700 dark:text-slate-300">
            {historyList.length === 0 ? "No Threat Inspections Yet" : "No Matching Filter Results"}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">
            {historyList.length === 0
              ? "Run a threat inspection on any e-commerce page to populate history logs."
              : "Try adjusting your search keywords or threat level filter."}
          </p>
        </div>
      ) : (
        <div className="space-y-2.5" role="list" aria-label="Investigation history list">
          {filteredHistory.map((item) => (
            <div
              key={item.id}
              role="listitem"
              className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-2 transition-all hover:border-purple-300 dark:hover:border-purple-800"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="space-y-1 min-w-0 flex-1">
                  <span
                    className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded uppercase inline-block ${
                      item.threatLevel === "CRITICAL" || item.threatLevel === "HIGH"
                        ? "bg-red-100 text-red-700 border border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800"
                        : item.threatLevel === "MEDIUM"
                        ? "bg-amber-100 text-amber-700 border border-amber-200 dark:bg-amber-950 dark:text-amber-300 dark:border-amber-800"
                        : "bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800"
                    }`}
                  >
                    {item.threatLevel} (Risk: {item.riskScore})
                  </span>
                  <h3 className="text-xs font-semibold text-slate-900 dark:text-white leading-tight break-words" title={item.productTitle}>
                    {item.productTitle}
                  </h3>
                </div>

                <button
                  onClick={() => onDeleteRecord(item.id)}
                  className="text-slate-400 hover:text-red-600 dark:hover:text-red-400 p-1 rounded transition-colors shrink-0"
                  aria-label={`Delete record ${item.id}`}
                  title="Delete record"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>

              <div className="flex flex-wrap items-center justify-between gap-1.5 text-[10px] font-mono text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-800">
                <span className="bg-slate-100 dark:bg-slate-950 px-1.5 py-0.5 rounded border border-slate-200 dark:border-slate-800 text-purple-700 dark:text-purple-300 font-bold">
                  {item.marketplace}
                </span>
                <span className="truncate max-w-[140px]" title={item.sellerName}>Seller: {item.sellerName}</span>
                <span>{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>

              {item.investigationId && (
                <div className="flex items-center justify-between pt-1">
                  <span className="text-[9px] font-mono text-slate-400 truncate">ID: {item.investigationId}</span>
                  <button
                    onClick={() => onOpenDashboardReport(item.investigationId)}
                    className="inline-flex items-center gap-1 text-[10px] font-mono font-bold text-purple-700 dark:text-purple-300 hover:underline"
                  >
                    View Report <ExternalLink className="h-2.5 w-2.5" />
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
});

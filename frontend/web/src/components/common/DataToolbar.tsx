import { Button } from "./Button";
import { Search, Filter, ArrowUpDown, Calendar, RefreshCcw, Download } from "lucide-react";
import { cn } from "../../utils/cn";

interface DataToolbarProps {
  onSearch?: (value: string) => void;
  onFilter?: () => void;
  onSort?: () => void;
  onDateRange?: () => void;
  onRefresh?: () => void;
  onExport?: () => void;
  searchPlaceholder?: string;
  className?: string;
}

export function DataToolbar({
  onSearch,
  onFilter,
  onSort,
  onDateRange,
  onRefresh,
  onExport,
  searchPlaceholder = "Search...",
  className
}: DataToolbarProps) {
  return (
    <div className={cn("flex flex-col sm:flex-row items-center justify-between gap-4 p-3 bg-surface border border-border rounded-xl shadow-sm", className)}>
      <div className="flex-1 w-full sm:w-auto relative">
        {onSearch && (
          <>
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
            <input
              type="text"
              placeholder={searchPlaceholder}
              onChange={(e) => onSearch(e.target.value)}
              className="w-full sm:max-w-md h-9 pl-9 pr-4 rounded-md border border-border bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-shadow"
            />
          </>
        )}
      </div>

      <div className="flex items-center gap-2 overflow-x-auto w-full sm:w-auto hide-scrollbar">
        {onFilter && (
          <Button variant="outline" size="sm" onClick={onFilter}>
            <Filter className="mr-2 h-4 w-4" /> Filter
          </Button>
        )}
        {onSort && (
          <Button variant="outline" size="sm" onClick={onSort}>
            <ArrowUpDown className="mr-2 h-4 w-4" /> Sort
          </Button>
        )}
        {onDateRange && (
          <Button variant="outline" size="sm" onClick={onDateRange}>
            <Calendar className="mr-2 h-4 w-4" /> Date
          </Button>
        )}
        {(onRefresh || onExport) && (
          <div className="flex items-center gap-1 border-l border-border pl-2 ml-2">
            {onRefresh && (
              <Button variant="ghost" size="sm" onClick={onRefresh} title="Refresh">
                <RefreshCcw className="h-4 w-4" />
              </Button>
            )}
            {onExport && (
              <Button variant="ghost" size="sm" onClick={onExport} title="Export">
                <Download className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

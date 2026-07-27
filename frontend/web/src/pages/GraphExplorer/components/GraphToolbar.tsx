import { Button } from "../../../components/common/Button";
import { Search, ZoomIn, ZoomOut, Maximize, RefreshCcw, Filter } from "lucide-react";

interface GraphToolbarProps {
  currentLayout: string;
  onLayoutChange: (layout: string) => void;
  onRefresh: () => void;
}

export function GraphToolbar({ currentLayout, onLayoutChange, onRefresh }: GraphToolbarProps) {
  const layouts = [
    { id: "cose", label: "Force Directed" },
    { id: "concentric", label: "Circular" },
    { id: "grid", label: "Grid" },
    { id: "breadthfirst", label: "Hierarchical" }
  ];

  return (
    <div className="flex flex-col md:flex-row items-center justify-between gap-4 p-4 bg-surface border border-border rounded-xl shadow-sm mb-4">
      <div className="flex items-center gap-4 w-full md:w-auto">
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
          <input
            type="text"
            placeholder="Search nodes..."
            className="w-full h-9 pl-9 pr-4 rounded-md border border-border bg-slate-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>
        <Button variant="outline" size="sm" className="shrink-0" onClick={onRefresh}>
          <RefreshCcw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto pb-2 md:pb-0 hide-scrollbar">
        <div className="flex items-center bg-slate-100 p-1 rounded-lg border border-border mr-2">
          {layouts.map(layout => (
            <button
              key={layout.id}
              onClick={() => onLayoutChange(layout.id)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                currentLayout === layout.id
                  ? 'bg-white shadow-sm text-slate-900'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200'
              }`}
            >
              {layout.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1 border-l border-border pl-2">
          <Button variant="ghost" size="sm" title="Zoom In">
            <ZoomIn className="h-4 w-4 text-slate-700" />
          </Button>
          <Button variant="ghost" size="sm" title="Zoom Out">
            <ZoomOut className="h-4 w-4 text-slate-700" />
          </Button>
          <Button variant="ghost" size="sm" title="Fit Graph">
            <Maximize className="h-4 w-4 text-slate-700" />
          </Button>
          <Button variant="ghost" size="sm" title="Filter">
            <Filter className="h-4 w-4 text-slate-700" />
          </Button>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import { PageHeader } from "../../components/common/PageHeader";
import { LoadingSkeleton } from "../../components/common/LoadingSkeleton";
import { ErrorState } from "../../components/common/ErrorState";
import { useGraphData } from "./hooks/useGraph";
import { GraphCanvas } from "../../components/graph/GraphCanvas";
import { GraphToolbar } from "./components/GraphToolbar";
import { NodeInspector } from "./components/NodeInspector";

export default function GraphExplorer() {
  const [layout, setLayout] = useState("cose");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useGraphData();

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] pb-4">
      <div className="shrink-0">
        <PageHeader
          title="Knowledge Graph Explorer"
          description="Visually navigate semantic relationships, fraud networks, and organizational memory."
        />
        <GraphToolbar
          currentLayout={layout}
          onLayoutChange={setLayout}
          onRefresh={refetch}
        />
      </div>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row gap-4">
        <div className="flex-1 min-h-[400px] lg:min-h-0 relative">
          {isLoading ? (
            <LoadingSkeleton className="h-full w-full rounded-xl" />
          ) : isError || !data ? (
            <div className="h-full border border-border rounded-xl flex items-center justify-center bg-surface">
              <ErrorState message="Failed to load graph data" onRetry={() => refetch()} />
            </div>
          ) : (
            <GraphCanvas
              data={data}
              layoutName={layout}
              selectedNodeId={selectedNodeId}
              onNodeSelect={setSelectedNodeId}
            />
          )}
        </div>
        <div className="w-full lg:w-[400px] shrink-0 h-[400px] lg:h-full overflow-hidden">
          <NodeInspector nodeId={selectedNodeId} />
        </div>
      </div>
    </div>
  );
}

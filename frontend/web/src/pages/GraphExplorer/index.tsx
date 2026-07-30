import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../../components/common/PageHeader";
import { LoadingSkeleton } from "../../components/common/LoadingSkeleton";
import { ErrorState } from "../../components/common/ErrorState";
import { useGraph } from "./hooks/useGraph";
import { GraphCanvas } from "../../components/graph/GraphCanvas";
import { GraphToolbar } from "./components/GraphToolbar";
import { NodeInspector } from "./components/NodeInspector";
import { EntityDetailsDrawer, GraphNodeDetails } from "./components/EntityDetailsDrawer";

export default function GraphExplorer() {
  const navigate = useNavigate();
  const [layout, setLayout] = useState("cose");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [inspectedNode, setInspectedNode] = useState<GraphNodeDetails | null>(null);

  const { data, isLoading, isError, refetch } = useGraph();

  const handleNodeSelect = (nodeId: string | null) => {
    setSelectedNodeId(nodeId);
    if (nodeId && data?.nodes) {
      const match = data.nodes.find((n) => n.id === nodeId);
      if (match) {
        setInspectedNode({
          id: match.id,
          label: match.label || "Entity",
          name: match.label || match.id,
          type: match.type || "Entity",
          confidence: 0.92,
          risk_score: match.riskScore || 50,
          properties: match.properties,
        });
      }
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] pb-4 text-slate-900 dark:text-white">
      {/* Drawer */}
      <EntityDetailsDrawer
        node={inspectedNode}
        onClose={() => setInspectedNode(null)}
        onNavigateSearch={(query) => navigate(`/product-intelligence`)}
      />

      <div className="shrink-0">
        <PageHeader
          title="Threat Knowledge Graph Explorer"
          description="Visually navigate semantic relationships, fraud networks, shared GST/phones, and continuous investigation memory."
        />
        <GraphToolbar
          currentLayout={layout}
          onLayoutChange={setLayout}
          onRefresh={refetch}
        />
      </div>

      <div className="flex-1 min-h-0 flex flex-col lg:flex-row gap-4 mt-3">
        <div className="flex-1 min-h-[400px] lg:min-h-0 relative">
          {isLoading ? (
            <LoadingSkeleton className="h-full w-full rounded-xl" />
          ) : isError || !data ? (
            <div className="h-full border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center bg-white dark:bg-slate-900">
              <ErrorState message="Failed to load threat graph data" onRetry={() => refetch()} />
            </div>
          ) : (
            <GraphCanvas
              data={data}
              layoutName={layout}
              selectedNodeId={selectedNodeId}
              onNodeSelect={handleNodeSelect}
            />
          )}
        </div>
        <div className="w-full lg:w-[380px] shrink-0 h-[400px] lg:h-full overflow-hidden">
          <NodeInspector nodeId={selectedNodeId} />
        </div>
      </div>
    </div>
  );
}

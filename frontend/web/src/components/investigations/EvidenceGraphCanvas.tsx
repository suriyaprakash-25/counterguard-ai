import React, { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
import { GitCommit, ShieldAlert, Layers, Eye, RefreshCw } from "lucide-react";
import { EvidenceGraphDTO, EvidenceNodeData } from "../../types/investigations";

interface EvidenceGraphCanvasProps {
  graphData?: EvidenceGraphDTO;
}

export const EvidenceGraphCanvas: React.FC<EvidenceGraphCanvasProps> = ({ graphData }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedNode, setSelectedNode] = useState<EvidenceNodeData | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>("ALL");

  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];

  useEffect(() => {
    if (!containerRef.current) return;

    // Destroy existing instance if re-rendering
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    const elements: cytoscape.ElementDefinition[] = [];

    // Filter nodes by category if selected
    const filteredNodes = filterCategory === "ALL"
      ? nodes
      : nodes.filter(n => (n.data.category || "").toUpperCase() === filterCategory);

    const validNodeIds = new Set(filteredNodes.map(n => n.data.id));

    filteredNodes.forEach((n) => {
      elements.push({
        data: {
          id: n.data.id,
          label: `${n.data.agent}: ${n.data.label}`,
          category: n.data.category,
          severity: n.data.severity,
          confidence: n.data.confidence,
          agent: n.data.agent,
          description: n.data.description,
          timestamp: n.data.timestamp
        }
      });
    });

    edges.forEach((e) => {
      if (validNodeIds.has(e.data.source) && validNodeIds.has(e.data.target)) {
        elements.push({
          data: {
            id: e.data.id,
            source: e.data.source,
            target: e.data.target,
            relationship: e.data.relationship
          }
        });
      }
    });

    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: "node",
          style: {
            "background-color": "mapData(confidence, 0, 1, #ef4444, #10b981)",
            "label": "data(label)",
            "color": "#f8fafc",
            "font-size": "11px",
            "text-valign": "bottom",
            "text-margin-y": 5,
            "width": 32,
            "height": 32,
            "border-width": 2,
            "border-color": "#3b82f6"
          }
        },
        {
          selector: 'node[severity = "critical"]',
          style: { "border-color": "#dc2626", "border-width": 3 }
        },
        {
          selector: 'node[severity = "high"]',
          style: { "border-color": "#ea580c", "border-width": 3 }
        },
        {
          selector: "edge",
          style: {
            "width": 2,
            "line-color": "#64748b",
            "target-arrow-color": "#64748b",
            "target-arrow-shape": "triangle",
            "curve-style": "bezier"
          }
        },
        {
          selector: 'edge[relationship = "derived_from"]',
          style: {
            "line-style": "dashed",
            "line-color": "#3b82f6",
            "target-arrow-color": "#3b82f6"
          }
        },
        {
          selector: 'edge[relationship = "supports"]',
          style: {
            "line-style": "solid",
            "line-color": "#10b981",
            "target-arrow-color": "#10b981"
          }
        },
        {
          selector: 'edge[relationship = "conflicts_with"]',
          style: {
            "line-style": "solid",
            "line-color": "#ef4444",
            "target-arrow-color": "#ef4444"
          }
        }
      ],
      layout: {
        name: "breadthfirst",
        directed: true,
        padding: 20,
        spacingFactor: 1.25
      }
    });

    cy.on("tap", "node", (evt) => {
      const nodeData = evt.target.data();
      setSelectedNode(nodeData as EvidenceNodeData);
    });

    cyRef.current = cy;

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [graphData, filterCategory]);

  const categories = ["ALL", "PRICE", "SELLER", "BRAND", "SPECIFICATION", "METADATA", "REVIEWS"];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <GitCommit className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-slate-100 text-lg">Directed Evidence Relationship Graph</h3>
          <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full border border-indigo-500/30">
            {nodes.length} Nodes &bull; {edges.length} Edges
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Filter Category:</span>
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-xs text-slate-200 rounded-lg px-2.5 py-1 focus:outline-none focus:border-indigo-500"
          >
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>
      </div>

      {nodes.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 bg-slate-950/40 rounded-lg border border-slate-800/60">
          <Layers className="w-8 h-8 mb-2 opacity-50" />
          <p className="text-sm">No directed evidence graph elements to render.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
          <div className="lg:col-span-3 bg-slate-950/80 border border-slate-800 rounded-lg h-80 relative overflow-hidden">
            <div ref={containerRef} className="w-full h-full" />
            <div className="absolute bottom-2 left-2 flex items-center gap-3 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-md text-[10px] text-slate-400">
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span> Derived From
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block"></span> Supports
              </span>
              <span className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-rose-500 inline-block"></span> Conflicts With
              </span>
            </div>
          </div>

          <div className="bg-slate-950/50 border border-slate-800 rounded-lg p-3 text-xs space-y-3">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <span className="font-medium text-slate-300 flex items-center gap-1.5">
                <Eye className="w-3.5 h-3.5 text-indigo-400" /> Selected Node Lineage
              </span>
            </div>

            {selectedNode ? (
              <div className="space-y-2">
                <div>
                  <span className="text-[10px] uppercase text-slate-500 font-semibold">Title</span>
                  <p className="text-slate-200 font-medium">{selectedNode.label}</p>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 font-semibold">Agent Attribution</span>
                  <p className="text-indigo-300">{selectedNode.agent}</p>
                </div>
                <div className="flex justify-between">
                  <div>
                    <span className="text-[10px] uppercase text-slate-500 font-semibold">Category</span>
                    <p className="text-slate-300">{selectedNode.category}</p>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase text-slate-500 font-semibold">Confidence</span>
                    <p className="text-emerald-400 font-semibold">{(selectedNode.confidence * 100).toFixed(0)}%</p>
                  </div>
                </div>
                <div>
                  <span className="text-[10px] uppercase text-slate-500 font-semibold">Observation</span>
                  <p className="text-slate-400 text-[11px] leading-snug">{selectedNode.description}</p>
                </div>
              </div>
            ) : (
              <p className="text-slate-500 text-[11px] italic">
                Click on any node in the graph to inspect evidence lineage and details.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

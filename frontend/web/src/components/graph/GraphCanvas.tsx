import { useEffect, useRef } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import type { Core, ElementDefinition } from "cytoscape";
import type { GraphData } from "../../pages/GraphExplorer/models/graph";

interface GraphCanvasProps {
  data: GraphData;
  layoutName: string;
  onNodeSelect: (nodeId: string | null) => void;
  selectedNodeId: string | null;
}

export function GraphCanvas({ data, layoutName, onNodeSelect, selectedNodeId }: GraphCanvasProps) {
  const cyRef = useRef<Core | null>(null);

  const elements: ElementDefinition[] = [
    ...data.nodes.map(node => ({
      data: {
        id: node.id,
        label: node.label,
        type: node.type,
        riskScore: node.riskScore
      }
    })),
    ...data.edges.map(edge => ({
      data: {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label
      }
    }))
  ];

  const layout = {
    name: layoutName,
    animate: true,
    animationDuration: 500,
    fit: true,
    padding: 30
  };

  const stylesheet = [
    {
      selector: "node",
      style: {
        "background-color": (ele: any) => {
          const type = ele.data("type");
          if (type === "seller") return "#ef4444"; // red
          if (type === "product") return "#3b82f6"; // blue
          if (type === "phone") return "#f59e0b"; // amber
          if (type === "marketplace") return "#10b981"; // green
          if (type === "investigation") return "#8b5cf6"; // purple
          return "#94a3b8"; // slate
        },
        "label": "data(label)",
        "color": "#1e293b",
        "text-valign": "bottom",
        "text-margin-y": 8,
        "font-size": "12px",
        "font-family": "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial, \"Noto Sans\", sans-serif, \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Segoe UI Symbol\", \"Noto Color Emoji\"",
        "font-weight": "600",
        "text-outline-color": "#ffffff",
        "text-outline-width": 2,
        "width": (ele: any) => ele.data("riskScore") > 90 ? 40 : 30,
        "height": (ele: any) => ele.data("riskScore") > 90 ? 40 : 30,
        "border-width": 2,
        "border-color": "#ffffff",
        "shadow-blur": 10,
        "shadow-color": "#000",
        "shadow-opacity": 0.1,
        "shadow-offset-x": 0,
        "shadow-offset-y": 4
      }
    },
    {
      selector: "edge",
      style: {
        "width": 2,
        "line-color": "#cbd5e1",
        "target-arrow-color": "#cbd5e1",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "label": "data(label)",
        "font-size": "10px",
        "text-background-opacity": 1,
        "text-background-color": "#ffffff",
        "text-background-padding": 2,
        "color": "#64748b"
      }
    },
    {
      selector: ".highlighted",
      style: {
        "border-color": "#3b82f6",
        "border-width": 4,
        "line-color": "#3b82f6",
        "target-arrow-color": "#3b82f6",
        "z-index": 10
      }
    },
    {
      selector: ".faded",
      style: {
        "opacity": 0.2
      }
    }
  ];

  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      onNodeSelect(node.id());
    });

    cy.on("tap", (evt) => {
      if (evt.target === cy) {
        onNodeSelect(null);
      }
    });

    return () => {
      cy.removeAllListeners();
    };
  }, [onNodeSelect]);

  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    cy.elements().removeClass("highlighted faded");

    if (selectedNodeId) {
      const selected = cy.getElementById(selectedNodeId);
      if (selected.length > 0) {
        const neighbors = selected.neighborhood();
        cy.elements().addClass("faded");
        selected.removeClass("faded").addClass("highlighted");
        neighbors.removeClass("faded").addClass("highlighted");
      }
    }
  }, [selectedNodeId, data]); // Re-run if data or selectedNodeId changes

  return (
    <div className="w-full h-full bg-slate-50 relative rounded-xl border border-border overflow-hidden shadow-inner">
      <CytoscapeComponent
        elements={elements}
        style={{ width: "100%", height: "100%" }}
        stylesheet={stylesheet as any}
        layout={layout}
        cy={(cy) => { cyRef.current = cy; }}
        wheelSensitivity={0.2}
      />
    </div>
  );
}

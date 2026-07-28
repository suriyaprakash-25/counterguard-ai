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

  const layout = layoutName ? {
    name: layoutName,
    animate: true,
    animationDuration: 500,
    fit: true,
    padding: 40
  } : (data.layout || { name: 'cose', fit: true, padding: 40, animate: true });

  const stylesheet = [
    {
      selector: "node",
      style: {
        "background-color": (ele: any) => {
          const type = ele.data("type");
          if (type === "seller") return "#ef4444";      // red
          if (type === "product") return "#3b82f6";     // blue
          if (type === "phone") return "#f59e0b";       // amber
          if (type === "marketplace") return "#10b981"; // green
          if (type === "investigation") return "#8b5cf6"; // purple
          return "#94a3b8";                             // slate
        },
        "label": "data(label)",
        "color": "#0f172a",
        "text-valign": "bottom",
        "text-margin-y": 6,
        "font-size": "11px",
        "font-family": "ui-sans-serif, system-ui, -apple-system, sans-serif",
        "font-weight": "700",
        "text-outline-color": "#ffffff",
        "text-outline-width": 2,
        "text-wrap": "wrap",
        "text-max-width": "100px",
        "width": (ele: any) => ele.data("riskScore") > 80 ? 38 : 28,
        "height": (ele: any) => ele.data("riskScore") > 80 ? 38 : 28,
        "border-width": 2,
        "border-color": "#ffffff",
        "transition-property": "background-color, border-color, border-width, opacity",
        "transition-duration": "0.3s"
      }
    },
    {
      selector: "edge",
      style: {
        "width": 1.5,
        "line-color": "#cbd5e1",
        "target-arrow-color": "#cbd5e1",
        "target-arrow-shape": "triangle",
        "curve-style": "bezier",
        "label": "data(label)",
        "font-size": "9px",
        "text-background-opacity": 0.9,
        "text-background-color": "#ffffff",
        "text-background-padding": 2,
        "color": "#475569"
      }
    },
    {
      selector: ".highlighted",
      style: {
        "border-color": "#2563eb",
        "border-width": 4,
        "line-color": "#2563eb",
        "target-arrow-color": "#2563eb",
        "width": 3,
        "z-index": 999,
        "opacity": 1.0
      }
    },
    {
      selector: ".faded",
      style: {
        "opacity": 0.15
      }
    },
    {
      selector: ".low-zoom label",
      style: {
        "label": ""
      }
    }
  ];

  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    // Zoom-based label thresholding to prevent visual crowding
    const handleZoom = () => {
      if (cy.zoom() < 0.65) {
        cy.elements().addClass("low-zoom");
      } else {
        cy.elements().removeClass("low-zoom");
      }
    };

    cy.on("zoom", handleZoom);

    cy.on("tap", "node", (evt) => {
      const node = evt.target;
      onNodeSelect(node.id());

      // Animated focus on selected node
      cy.animate({
        center: { eles: node },
        zoom: Math.max(cy.zoom(), 1.1),
        duration: 350
      });
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

    cy.resize();
    cy.fit(undefined, 40);

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
  }, [selectedNodeId, data, layoutName]);

  return (
    <div className="w-full h-full min-h-[380px] bg-slate-50 relative rounded-xl border border-border overflow-hidden shadow-inner">
      <CytoscapeComponent
        elements={elements}
        style={{ width: "100%", height: "100%" }}
        stylesheet={stylesheet as any}
        layout={layout}
        cy={(cy) => {
          cyRef.current = cy;
        }}
      />
    </div>
  );
}

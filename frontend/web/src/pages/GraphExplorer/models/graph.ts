export interface GraphNode {
  id: string;
  label: string;
  type: "seller" | "product" | "marketplace" | "phone" | "invoice" | "image" | "brand" | "investigation" | "pattern" | "memory";
  riskScore?: number;
  properties?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  weight?: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphStatistics {
  totalNodes: number;
  totalEdges: number;
  communities: number;
  largestComponent: number;
  averageDegree: number;
  mostConnectedSeller: string;
}

export interface NodeDetails {
  node: GraphNode;
  degree: number;
  relatedInvestigations: number;
  confidence: number;
  connectedEntities: Array<{ id: string, label: string, type: string, relationship: string }>;
}

export interface IntelligenceSummary {
  knownSellers: number;
  knownFraudRings: number;
  knownCounterfeitListings: number;
  repeatedAssets: number;
  historicalInvestigations: number;
  memoryEpisodes: number;
  graphNodes: number;
  graphRelationships: number;
}

export interface KnownSeller {
  id: string;
  name: string;
  marketplace: string;
  riskScore: number;
  historicalInvestigations: number;
  connectedFraudRings: string[];
  status: "active" | "banned" | "monitoring";
}

export interface FraudRing {
  id: string;
  name: string;
  members: number;
  averageRisk: number;
  connectedListings: number;
  connectedSellers: number;
  lastActivity: string;
}

export interface KnownPattern {
  id: string;
  type: "description" | "invoice" | "pricing" | "phone" | "seller" | "brand_abuse" | "image";
  title: string;
  occurrences: number;
  description: string;
}

export interface ImageCluster {
  id: string;
  thumbnailUrl: string;
  occurrences: number;
  connectedSellers: number;
  connectedListings: number;
  similarityScore: number;
  evidenceCount: number;
}

export interface PhoneCluster {
  id: string;
  phoneNumber: string;
  occurrences: number;
  connectedSellers: number;
  riskScore: number;
}

export interface InvoiceCluster {
  id: string;
  invoiceId: string;
  occurrences: number;
  associatedSellers: number;
  marketplace: string;
  historicalRisk: number;
}

export interface MemoryInsight {
  id: string;
  title: string;
  description: string;
  confidence: number;
  type: "similar_investigation" | "new_pattern" | "high_confidence_episode";
  context: string;
}

export interface KnowledgeGraphStats {
  nodeCount: number;
  relationshipCount: number;
  communities: number;
  largestFraudRingSize: number;
  averageConnectivity: number;
  graphDensity: number;
}

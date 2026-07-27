import type {
  IntelligenceSummary,
  KnownSeller,
  FraudRing,
  KnownPattern,
  ImageCluster,
  PhoneCluster,
  InvoiceCluster,
  MemoryInsight,
  KnowledgeGraphStats
} from "../models/intelligence";
import type { IntelligenceSummaryDTO } from "./intelligence.mock";

export const IntelligenceMapper = {
  toSummary(dto: IntelligenceSummaryDTO): IntelligenceSummary {
    return {
      knownSellers: dto.total_sellers,
      knownFraudRings: dto.total_rings,
      knownCounterfeitListings: dto.total_listings,
      repeatedAssets: dto.total_assets,
      historicalInvestigations: dto.total_investigations,
      memoryEpisodes: dto.total_episodes,
      graphNodes: dto.nodes,
      graphRelationships: dto.relationships
    };
  },

  toSellers(dtos: any[]): KnownSeller[] {
    return dtos.map(dto => ({
      id: dto.id,
      name: dto.seller_name,
      marketplace: dto.platform,
      riskScore: dto.risk,
      historicalInvestigations: dto.inv_count,
      connectedFraudRings: dto.rings,
      status: dto.state
    }));
  },

  toRings(dtos: any[]): FraudRing[] {
    return dtos.map(dto => ({
      id: dto.id,
      name: dto.ring_name,
      members: dto.member_count,
      averageRisk: dto.avg_risk,
      connectedListings: dto.listings,
      connectedSellers: dto.sellers,
      lastActivity: dto.last_seen
    }));
  },

  toPatterns(dtos: any[]): KnownPattern[] {
    return dtos.map(dto => ({
      id: dto.id,
      type: dto.pattern_type,
      title: dto.name,
      occurrences: dto.count,
      description: dto.desc
    }));
  },

  toImageClusters(dtos: any[]): ImageCluster[] {
    return dtos.map(dto => ({
      id: dto.id,
      thumbnailUrl: dto.url,
      occurrences: dto.count,
      connectedSellers: dto.sellers,
      connectedListings: dto.listings,
      similarityScore: dto.similarity,
      evidenceCount: dto.evidence
    }));
  },

  toPhoneClusters(dtos: any[]): PhoneCluster[] {
    return dtos.map(dto => ({
      id: dto.id,
      phoneNumber: dto.phone,
      occurrences: dto.count,
      connectedSellers: dto.sellers,
      riskScore: dto.risk
    }));
  },

  toInvoiceClusters(dtos: any[]): InvoiceCluster[] {
    return dtos.map(dto => ({
      id: dto.id,
      invoiceId: dto.doc_id,
      occurrences: dto.count,
      associatedSellers: dto.sellers,
      marketplace: dto.platform,
      historicalRisk: dto.risk
    }));
  },

  toMemoryInsights(dtos: any[]): MemoryInsight[] {
    return dtos.map(dto => ({
      id: dto.id,
      title: dto.title,
      description: dto.desc,
      confidence: dto.conf,
      type: dto.type,
      context: dto.ctx
    }));
  },

  toGraphStats(dto: any): KnowledgeGraphStats {
    return {
      nodeCount: dto.n_count,
      relationshipCount: dto.r_count,
      communities: dto.comm_count,
      largestFraudRingSize: dto.max_ring,
      averageConnectivity: dto.avg_conn,
      graphDensity: dto.density
    };
  }
};

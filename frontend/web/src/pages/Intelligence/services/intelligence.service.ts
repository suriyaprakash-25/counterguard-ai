import { IntelligenceMapper } from "./intelligence.mapper";
import {
  MOCK_SUMMARY_DTO,
  MOCK_SELLERS_DTO,
  MOCK_RINGS_DTO,
  MOCK_PATTERNS_DTO,
  MOCK_IMAGE_CLUSTERS_DTO,
  MOCK_PHONE_CLUSTERS_DTO,
  MOCK_INVOICE_CLUSTERS_DTO,
  MOCK_MEMORY_INSIGHTS_DTO,
  MOCK_GRAPH_STATS_DTO
} from "./intelligence.mock";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const intelligenceService = {
  async getSummary() {
    await delay(600);
    return IntelligenceMapper.toSummary(MOCK_SUMMARY_DTO);
  },

  async getKnownSellers() {
    await delay(1000);
    return IntelligenceMapper.toSellers(MOCK_SELLERS_DTO);
  },

  async getFraudRings() {
    await delay(1200);
    return IntelligenceMapper.toRings(MOCK_RINGS_DTO);
  },

  async getKnownPatterns() {
    await delay(800);
    return IntelligenceMapper.toPatterns(MOCK_PATTERNS_DTO);
  },

  async getRepeatedImages() {
    await delay(1400);
    return IntelligenceMapper.toImageClusters(MOCK_IMAGE_CLUSTERS_DTO);
  },

  async getRepeatedPhones() {
    await delay(900);
    return IntelligenceMapper.toPhoneClusters(MOCK_PHONE_CLUSTERS_DTO);
  },

  async getRepeatedInvoices() {
    await delay(1100);
    return IntelligenceMapper.toInvoiceClusters(MOCK_INVOICE_CLUSTERS_DTO);
  },

  async getMemoryInsights() {
    await delay(1300);
    return IntelligenceMapper.toMemoryInsights(MOCK_MEMORY_INSIGHTS_DTO);
  },

  async getKnowledgeGraphStats() {
    await delay(700);
    return IntelligenceMapper.toGraphStats(MOCK_GRAPH_STATS_DTO);
  }
};

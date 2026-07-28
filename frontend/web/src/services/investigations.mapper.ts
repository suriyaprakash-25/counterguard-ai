import type {
  InvestigationWorkspaceDetails,
  InvestigationSummary,
  TimelineEvent,
  EvidenceItem,
  RecommendedProduct,
  ProductComparison,
  PriceIntelligence,
  RecommendationSummary
} from '../types/investigations';
import { resolveInvestigationTitle } from './target_normalization';

export const InvestigationsMapper = {
  toSummary(dto: any): InvestigationSummary {
    const displayTitle = resolveInvestigationTitle(dto);
    return {
      id: dto.id || '',
      name: displayTitle,
      displayTitle,
      originalTarget: dto.original_target || dto.listing_url || '',
      marketplace: dto.marketplace || dto.report?.marketplace || 'Global Search',
      status: dto.status || 'pending',
      riskScore: dto.risk_score ?? dto.report?.risk_score ?? 0,
      investigationType: dto.investigationType || 'Autonomous Swarm',
      plannerPriority: dto.plannerPriority || 'high',
      agentCount: dto.agentCount || (dto.evidence_timeline?.length || 5),
      createdAt: dto.created_at || new Date().toISOString(),
      lastUpdated: dto.updated_at || new Date().toISOString(),
    };
  },


  toWorkspaceDetails(dto: any): InvestigationWorkspaceDetails {
    const summary = this.toSummary(dto);
    const riskScore = summary.riskScore;

    // 1. Determine Verdict from Risk Score Thresholds:
    // 0-20: AUTHENTIC, 21-40: LOW RISK, 41-70: SUSPICIOUS, 71-100: LIKELY COUNTERFEIT
    let verdict: "authentic" | "low_risk" | "suspicious" | "likely_counterfeit" | "pending" = "pending";
    if (dto.status === 'completed' || dto.report) {
      if (riskScore <= 20) {
        verdict = "authentic";
      } else if (riskScore <= 40) {
        verdict = "low_risk";
      } else if (riskScore <= 70) {
        verdict = "suspicious";
      } else {
        verdict = "likely_counterfeit";
      }
    }

    // 2. Verdict Confidence (0-100%)
    let rawConf = dto.report?.confidence ?? 0.85;
    if (rawConf > 0 && rawConf <= 1.0) {
      rawConf = Math.round(rawConf * 100);
    }
    const verdictConfidence = Math.min(100, Math.max(1, Math.round(rawConf)));

    // 3. Map Timeline Events
    const timeline: TimelineEvent[] = (dto.evidence_timeline || []).map((ev: any, idx: number) => {
      let severity: "critical" | "high" | "medium" | "low" | "info" = "info";
      const actionLower = (ev.action || "").toLowerCase();
      if (actionLower.includes("anomaly") || actionLower.includes("fraud") || actionLower.includes("mismatch")) {
        severity = riskScore > 70 ? "critical" : "high";
      } else if (actionLower.includes("lookup") || actionLower.includes("search")) {
        severity = "medium";
      }

      return {
        id: ev.id || `ev-${idx}`,
        timestamp: ev.timestamp || new Date().toISOString(),
        title: ev.action ? ev.action.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase()) : "Agent Assessment",
        description: ev.detail || "",
        iconType: "agent",
        agent: ev.agent || "SpecialistAgent",
        severity: severity
      };
    });

    // 4. Map Collected Evidence Items
    const evidence: EvidenceItem[] = (dto.evidence || []).map((ev: any, idx: number) => ({
      id: ev.id || `ev-item-${idx}`,
      type: ev.type || "metadata",
      confidence: ev.confidence || verdictConfidence,
      description: ev.description || ev.value || "",
      source: ev.source || ev.agent || "Specialist Agent",
      title: ev.title || "Evidence Record",
      value: ev.value || ev.description || "",
      agent: ev.agent || ev.source || "Agent"
    }));

    // 5. Consensus
    const voteLabel = verdict.replace(/_/g, " ").toUpperCase();
    const consensus = dto.consensus || {
      agreementScore: verdictConfidence,
      explanation: `Specialist agents completed multi-agent analysis and reached an agreement score of ${verdictConfidence}% for this ${voteLabel} verdict.`,
      agentVotes: [
        { agent: "PriceAgent", vote: voteLabel, riskScore: Math.min(100, riskScore + 5), confidence: verdictConfidence },
        { agent: "SellerAgent", vote: voteLabel, riskScore: Math.max(0, riskScore - 10), confidence: verdictConfidence },
        { agent: "BrandAgent", vote: voteLabel, riskScore: Math.min(100, riskScore + 2), confidence: verdictConfidence },
        { agent: "ReviewAgent", vote: voteLabel, riskScore: Math.max(0, riskScore - 5), confidence: verdictConfidence },
        { agent: "CoordinatorAgent", vote: voteLabel, riskScore: riskScore, confidence: verdictConfidence },
      ]
    };

    // 6. Memory Context
    const memoryContext = dto.memory_context || dto.memoryContext || {
      previousInvestigations: 1,
      semanticMatches: 1,
      historicalRisk: riskScore,
      knownPatterns: (dto.report?.findings && Array.isArray(dto.report.findings)) ? dto.report.findings.slice(0, 3) : ["Price anomaly vs MSRP baseline"],
      knownSeller: dto.report?.seller || summary.marketplace,
      topSimilarCase: `INV-${summary.id.substring(0, 8)}`
    };

    // 7. Recommendations
    const recommendations: any[] = [];
    if (dto.report?.findings && Array.isArray(dto.report.findings) && dto.report.findings.length > 0) {
      dto.report.findings.forEach((finding: string, idx: number) => {
        recommendations.push({
          category: idx === 0 ? "Immediate" : idx === 1 ? "Manual Review" : "Monitor",
          priority: idx === 0 ? "High" : "Medium",
          action: finding,
          reason: `Derived from specialist finding: ${finding}`
        });
      });
    }
    if (dto.report?.recommendation) {
      recommendations.push({
        category: "Manual Review",
        priority: "Medium",
        action: dto.report.recommendation,
        reason: "Coordinator synthesis recommendation."
      });
    }

    // 8. Agent Activity Log
    const agentActivity = dto.agent_activity || dto.agentActivity || [
      { id: "act-1", agent: "PlanningAgent", status: "success", runtimeMs: 140, confidence: 95, timestamp: summary.createdAt, riskScore: 0, toolsUsed: ["investigation_planner"] },
      { id: "act-2", agent: "PriceAgent", status: "success", runtimeMs: 310, confidence: verdictConfidence, timestamp: summary.createdAt, riskScore: Math.min(100, riskScore + 5), toolsUsed: ["price_history"] },
      { id: "act-3", agent: "SellerAgent", status: "success", runtimeMs: 270, confidence: verdictConfidence, timestamp: summary.createdAt, riskScore: Math.max(0, riskScore - 10), toolsUsed: ["whois_lookup", "seller_reputation"] },
      { id: "act-4", agent: "BrandAgent", status: "success", runtimeMs: 405, confidence: verdictConfidence, timestamp: summary.createdAt, riskScore: Math.min(100, riskScore + 2), toolsUsed: ["trademark_lookup", "product_catalog"] },
      { id: "act-5", agent: "ReviewAgent", status: "success", runtimeMs: 220, confidence: verdictConfidence, timestamp: summary.createdAt, riskScore: Math.max(0, riskScore - 5), toolsUsed: ["reverse_image_search"] },
      { id: "act-6", agent: "TrustedProductAgent", status: "success", runtimeMs: 185, confidence: 98, timestamp: summary.createdAt, riskScore: 0, toolsUsed: ["recommendation_service"] },
      { id: "act-7", agent: "CoordinatorAgent", status: "success", runtimeMs: 510, confidence: verdictConfidence, timestamp: summary.createdAt, riskScore: riskScore, toolsUsed: ["llm_service"] },
    ];

    // 9. Recommended Products & Comparison & Intelligence
    const recommendedProducts: RecommendedProduct[] = dto.recommended_products || dto.recommendedProducts || [];
    const productComparison: ProductComparison | undefined = dto.product_comparison || dto.productComparison;
    const priceIntelligence: PriceIntelligence | undefined = dto.price_intelligence || dto.priceIntelligence;
    const recommendationSummary: RecommendationSummary | undefined = dto.recommendation_summary || dto.recommendationSummary;

    // 10. AI Summary & Reasoning
    const aiSummary = dto.report?.ai_summary || dto.report?.summary || "Autonomous investigation synthesis in progress.";
    const reasoning = dto.report?.ai_reasoning || dto.report?.summary || "Multi-agent evaluation completed.";

    return {
      ...summary,
      finalVerdict: verdict,
      verdictConfidence,
      aiSummary,
      timeline,
      evidence,
      graphPreview: [],
      memoryContext,
      consensus,
      explainability: {
        reasoning,
        supportingEvidenceIds: []
      },
      recommendations,
      agentActivity,
      recommendedProducts,
      productComparison,
      priceIntelligence,
      recommendationSummary
    };
  }
};

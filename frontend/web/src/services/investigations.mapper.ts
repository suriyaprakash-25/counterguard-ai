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

    // 1. Determine Verdict from Risk Score Thresholds or INSUFFICIENT_DATA
    let verdict: "authentic" | "low_risk" | "suspicious" | "likely_counterfeit" | "pending" | "insufficient_data" = "pending";
    if (dto.status === 'failed' || dto.report?.final_verdict === 'INSUFFICIENT_DATA' || dto.report?.risk_level === 'INSUFFICIENT_DATA') {
      verdict = "insufficient_data" as any;
    } else if (dto.status === 'completed' || dto.report) {
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
    let verdictConfidence = 0;
    if (verdict !== ("insufficient_data" as any)) {
      let rawConf = dto.report?.confidence ?? 0.85;
      if (rawConf > 0 && rawConf <= 1.0) {
        rawConf = Math.round(rawConf * 100);
      }
      verdictConfidence = Math.min(100, Math.max(1, Math.round(rawConf)));
    }

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

    // 5. Consensus (HONEST: No synthetic fabrication)
    const consensus = (dto.status === 'failed' || verdict === ("insufficient_data" as any))
      ? null
      : (dto.consensus || dto.report?.consensus || null);

    // 6. Memory Context (HONEST: No synthetic fabrication)
    const memoryContext = (dto.status === 'failed' || verdict === ("insufficient_data" as any))
      ? null
      : (dto.memory_context || dto.memoryContext || null);

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

    // 8. Agent Activity Log (HONEST: No synthetic fabrication)
    const agentActivity = (dto.status === 'failed' || verdict === ("insufficient_data" as any))
      ? []
      : (dto.agent_activity || dto.agentActivity || []);

    // 9. Recommended Products & Comparison & Intelligence & Evidence Summary
    const recommendedProducts: RecommendedProduct[] = dto.recommended_products || dto.recommendedProducts || [];
    const productComparison: ProductComparison | undefined = dto.product_comparison || dto.productComparison;
    const priceIntelligence: PriceIntelligence | undefined = dto.price_intelligence || dto.priceIntelligence;
    const recommendationSummary: RecommendationSummary | undefined = dto.recommendation_summary || dto.recommendationSummary;
    const evidenceSummary: any = dto.report?.evidence_summary || dto.evidence_summary || null;

    const honestWarning = "Synthesis unavailable — insufficient evidence was collected for this investigation.";
    // Only show warning when investigation actually failed — never during in_progress/pending
    const dataConfidenceWarning: string | null = (dto.status === 'failed')
      ? honestWarning
      : (dto.report?.data_confidence_warning || dto.data_confidence_warning || null);

    // Only show warning when investigation actually failed — never during in_progress/pending
    const aiSummary = (dto.status === 'failed')
      ? honestWarning
      : (dto.report?.ai_summary || dto.report?.summary || "Autonomous investigation synthesis in progress.");
    const reasoning = (dto.status === 'failed')
      ? honestWarning
      : (dto.report?.ai_reasoning || dto.report?.summary || "Multi-agent evaluation completed.");

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
      recommendationSummary,
      evidenceSummary,
      dataConfidenceWarning
    };
  }
};

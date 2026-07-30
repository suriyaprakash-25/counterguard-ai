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
    const rawEvList = dto.context?.shared_evidence || dto.evidence || [];
    const evidence: EvidenceItem[] = rawEvList.map((ev: any, idx: number) => ({
      id: ev.evidence_id || ev.id || `ev-item-${idx}`,
      type: ev.type || "metadata",
      confidence: ev.confidence ?? (verdictConfidence / 100),
      description: ev.description || ev.content || ev.value || "",
      source: ev.source || ev.source_agent || ev.agent_name || ev.agent || "Specialist Agent",
      title: ev.title || "Evidence Record",
      value: ev.value || ev.description || "",
      agent: ev.agent_name || ev.source_agent || ev.agent || "Agent",
      agent_name: ev.agent_name || ev.source_agent || ev.agent || "Agent",
      category: ev.category || "General",
      severity: ev.severity || (riskScore > 70 ? "critical" : riskScore > 40 ? "high" : "medium"),
      timestamp: ev.timestamp || new Date().toISOString()
    }));

    // 5. Consensus
    const consensus = (dto.status === 'failed' || verdict === ("insufficient_data" as any))
      ? null
      : (dto.consensus || dto.report?.consensus || null);

    // 6. Memory Context
    const memoryContext = (dto.status === 'failed' || verdict === ("insufficient_data" as any))
      ? null
      : (dto.memory_context || dto.memoryContext || null);

    // 7. Recommendations
    const recommendations: any[] = dto.report?.recommended_actions || [];
    if (recommendations.length === 0 && dto.report?.findings && Array.isArray(dto.report.findings) && dto.report.findings.length > 0) {
      dto.report.findings.forEach((finding: string, idx: number) => {
        recommendations.push({
          category: idx === 0 ? "Immediate" : idx === 1 ? "Manual Review" : "Monitor",
          priority: idx === 0 ? "High" : "Medium",
          action: finding,
          reason: `Derived from specialist finding: ${finding}`
        });
      });
    }

    // 8. Agent Activity Log
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
    const dataConfidenceWarning: string | null = (dto.status === 'failed')
      ? honestWarning
      : (dto.report?.data_confidence_warning || dto.data_confidence_warning || null);

    const aiSummary = (dto.status === 'failed')
      ? honestWarning
      : (dto.report?.ai_summary || dto.report?.summary || "Autonomous investigation synthesis in progress.");
    const reasoning = (dto.status === 'failed')
      ? honestWarning
      : (dto.report?.ai_reasoning || dto.report?.reasoning || dto.report?.summary || "Multi-agent evaluation completed.");

    // Sprint 1 Evidence-Driven Reasoning & Shared Blackboard mappings
    const overallReasoning: string[] = dto.report?.overall_reasoning || [];
    const supportingEvidence: EvidenceItem[] = (dto.report?.supporting_evidence || []).map((e: any, idx: number) => ({
      id: e.evidence_id || e.id || `sup-ev-${idx}`,
      type: "metadata",
      confidence: e.confidence || 0.85,
      description: e.description || e.content || "",
      source: e.source || e.agent_name || "Specialist Agent",
      title: e.title || "Supporting Risk Factor",
      agent_name: e.agent_name || e.source_agent || "Agent",
      category: e.category || "General",
      severity: e.severity || "high",
      timestamp: e.timestamp || new Date().toISOString()
    }));

    const conflictingEvidence: EvidenceItem[] = (dto.report?.conflicting_evidence || []).map((e: any, idx: number) => ({
      id: e.evidence_id || e.id || `conf-ev-${idx}`,
      type: "metadata",
      confidence: e.confidence || 0.85,
      description: e.description || e.content || "",
      source: e.source || e.agent_name || "Specialist Agent",
      title: e.title || "Conflicting Factor",
      agent_name: e.agent_name || e.source_agent || "Agent",
      category: e.category || "General",
      severity: e.severity || "low",
      timestamp: e.timestamp || new Date().toISOString()
    }));

    const sharedContext = {
      observations: dto.context?.shared_observations || [],
      evidenceCount: rawEvList.length,
      confidenceHistory: dto.context?.confidence_timeline || dto.report?.confidence_timeline || [],
      agentContributions: agentActivity.map((a: any) => ({
        agent: a.agent || a.source || "Agent",
        status: a.status || "success",
        confidence: a.confidence || 0.85,
        runtimeMs: a.runtimeMs || 250,
        observations: `${a.agent} executed task successfully.`
      }))
    };

    const confidenceTimeline = dto.report?.confidence_timeline || dto.context?.confidence_timeline || [];
    const reasoningTimeline = dto.report?.reasoning_timeline || dto.context?.reasoning_timeline || [];
    const evidenceGraph = dto.report?.evidence_graph || dto.context?.evidence_graph || { nodes: [], edges: [] };

    return {
      id: dto.id || dto.investigation_id || "inv_unknown",
      name: dto.name || dto.display_title || "Investigation Target",
      displayTitle: dto.display_title || dto.name || "Target Product",
      originalTarget: dto.target_url || dto.original_target || "",
      marketplace: dto.marketplace || "Global",
      status: dto.status || "completed",
      riskScore: riskScore,
      investigationType: dto.investigation_type || "Autonomous Counterfeit Audit",
      plannerPriority: dto.planner_priority || "high",
      createdAt: dto.created_at || new Date().toISOString(),
      lastUpdated: dto.updated_at || new Date().toISOString(),
      agentCount: agentActivity.length || 7,
      verdict: verdict,
      verdictConfidence: verdictConfidence,
      verdictExplanation: reasoning,
      aiSummary: aiSummary,
      timeline: timeline,
      evidence: evidence,
      graphPreview: [],
      memoryContext: memoryContext,
      consensus: consensus,
      explainability: {
        reasoning: reasoning,
        supportingEvidenceIds: evidence.map(e => e.id)
      },
      recommendations: recommendations,
      agentActivity: agentActivity,
      recommendedProducts: recommendedProducts,
      productComparison: productComparison,
      priceIntelligence: priceIntelligence,
      recommendationSummary: recommendationSummary,
      evidenceSummary: evidenceSummary,
      dataConfidenceWarning: dataConfidenceWarning,
      overallReasoning: overallReasoning,
      supportingEvidence: supportingEvidence,
      conflictingEvidence: conflictingEvidence,
      confidenceTimeline: confidenceTimeline,
      reasoningTimeline: reasoningTimeline,
      evidenceGraph: evidenceGraph,
      sharedContext: sharedContext
    };
  }
};

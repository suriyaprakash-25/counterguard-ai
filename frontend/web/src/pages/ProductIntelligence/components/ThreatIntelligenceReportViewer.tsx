/**
 * ThreatIntelligenceReportViewer.tsx — Executive Threat Intelligence Report Viewer & Download Center
 * Supports PDF print, JSON export, CSV export, and Presentation Mode (Full-screen executive slide presentation).
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileText, Download, Presentation, ShieldAlert, CheckCircle2, ChevronRight, X, Sparkles, Network, Database } from 'lucide-react';
import { apiClient, endpoints } from '../../../shared/api';

export interface ThreatIntelligenceReportDTO {
  report_id: string;
  product_name: string;
  generated_at: string;
  executive_summary: string;
  threat_level: string;
  threat_score: number;
  fraud_ring_summary: string;
  historical_similarity: string;
  evidence_summary: string[];
  graph_insights: string;
  affected_marketplaces: string[];
  high_risk_sellers: Array<{ name: string; marketplace: string; risk_score: number; location?: string }>;
  recommendations: string[];
  enforcement_actions: string[];
  coordinator_reasoning: string;
}

export function ThreatIntelligenceReportViewer({ query = 'CMF Buds 2a' }: { query?: string }) {
  const [isPresentationOpen, setIsPresentationOpen] = useState(false);
  const [activeSlide, setActiveSlide] = useState(0);

  const { data: report, isLoading } = useQuery<ThreatIntelligenceReportDTO>({
    queryKey: ['intelligenceReport', query],
    queryFn: async () => {
      const resp = await apiClient.post(`${endpoints.threatReports.generate}`, { product_name: query });
      return resp.data;
    },
  });

  if (isLoading || !report) return null;

  // Export handlers
  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Threat_Intelligence_Report_${report.report_id}.json`;
    a.click();
  };

  const handleExportCSV = () => {
    let csv = `Report ID,Product,Threat Level,Threat Score,Generated At\n`;
    csv += `"${report.report_id}","${report.product_name}","${report.threat_level}",${report.threat_score},"${report.generated_at}"\n\n`;
    csv += `Evidence Findings\n`;
    report.evidence_summary.forEach((e) => { csv += `"${e.replace(/"/g, '""')}"\n`; });

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Threat_Intelligence_Report_${report.report_id}.csv`;
    a.click();
  };

  const handleExportPDF = () => {
    window.print();
  };

  const presentationSlides = [
    { title: 'Executive Overview', content: report.executive_summary, badge: `Threat Level: ${report.threat_level}` },
    { title: 'Fraud Ring & Syndicate Intelligence', content: report.fraud_ring_summary, badge: `${report.affected_marketplaces.length} Affected Marketplaces` },
    { title: 'Threat Knowledge Graph & Centrality', content: report.graph_insights, badge: `${report.high_risk_sellers.length} High Risk Merchants` },
    { title: 'Vector Memory & Historical Precedents', content: report.historical_similarity, badge: 'ChromaDB Organizational Memory' },
    { title: 'Strategic Recommendations & Legal Enforcement', content: report.recommendations.join(' • '), badge: 'Enforcement Actions Active' },
  ];

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 mb-6">
      {/* Header & Download / Presentation Center */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-violet-100 dark:bg-violet-950 text-violet-600 dark:text-violet-400">
            <FileText className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white">
              Executive Threat Intelligence Report — {report.product_name}
            </h2>
            <p className="text-xs text-slate-500 font-mono">Report ID: {report.report_id} • Generated {new Date(report.generated_at).toLocaleString()}</p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPresentationOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-violet-600 text-white hover:bg-violet-700 text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
          >
            <Presentation className="h-4 w-4" /> Presentation Mode
          </button>
          <button
            onClick={handleExportPDF}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold flex items-center gap-1.5"
          >
            <Download className="h-4 w-4" /> PDF
          </button>
          <button
            onClick={handleExportJSON}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold"
          >
            JSON
          </button>
          <button
            onClick={handleExportCSV}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 text-xs font-semibold"
          >
            CSV
          </button>
        </div>
      </div>

      {/* Report 11 Executive Sections */}
      <div className="space-y-5 text-xs text-slate-700 dark:text-slate-300">
        {/* Section 1: Executive Summary */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-1.5">
          <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500">1. Executive Summary</div>
          <p className="text-sm font-medium leading-relaxed text-slate-900 dark:text-slate-100">{report.executive_summary}</p>
        </div>

        {/* Section 2 & 3: Fraud Ring & Historical Similarity */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-1.5">
            <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500">2. Active Fraud Ring Intelligence</div>
            <p className="leading-relaxed">{report.fraud_ring_summary}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-1.5">
            <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500">3. Vector Memory Precedents</div>
            <p className="leading-relaxed">{report.historical_similarity}</p>
          </div>
        </div>

        {/* Section 4: Evidence Findings */}
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-2">
          <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500">4. Key Evidence Findings</div>
          <div className="space-y-1.5">
            {report.evidence_summary.map((ev, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <CheckCircle2 className="h-4 w-4 text-violet-600 dark:text-violet-400 shrink-0 mt-0.5" />
                <span>{ev}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Section 5: Recommendations & Enforcement */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-1.5">
            <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500">5. Strategic Risk Recommendations</div>
            <ul className="list-disc pl-4 space-y-1">
              {report.recommendations.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 space-y-1.5">
            <div className="font-bold uppercase tracking-wider text-[11px] text-slate-500">6. Legal Enforcement Actions</div>
            <ul className="list-disc pl-4 space-y-1 font-semibold text-emerald-700 dark:text-emerald-400">
              {report.enforcement_actions.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Full-Screen Presentation Mode Modal */}
      {isPresentationOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/95 text-white flex flex-col justify-between p-8 backdrop-blur-md animate-in fade-in duration-200">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div className="flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-violet-400" />
              <span className="text-sm font-bold uppercase tracking-wider text-slate-400">Executive Briefing Slide {activeSlide + 1} / {presentationSlides.length}</span>
            </div>
            <button
              onClick={() => setIsPresentationOpen(false)}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <div className="max-w-4xl mx-auto space-y-6 text-center py-12">
            <span className="px-4 py-1 rounded-full text-xs font-bold bg-violet-900 text-violet-200 border border-violet-700">
              {presentationSlides[activeSlide].badge}
            </span>
            <h1 className="text-3xl font-extrabold text-white">{presentationSlides[activeSlide].title}</h1>
            <p className="text-lg text-slate-300 leading-relaxed font-medium">
              {presentationSlides[activeSlide].content}
            </p>
          </div>

          <div className="flex items-center justify-between border-t border-slate-800 pt-4 max-w-4xl mx-auto w-full">
            <button
              disabled={activeSlide === 0}
              onClick={() => setActiveSlide((prev) => Math.max(0, prev - 1))}
              className="px-4 py-2 rounded-lg bg-slate-800 disabled:opacity-40 text-xs font-bold"
            >
              Previous Slide
            </button>
            <span className="text-xs text-slate-500 font-mono">CounterGuard Threat Intelligence Engine</span>
            <button
              disabled={activeSlide === presentationSlides.length - 1}
              onClick={() => setActiveSlide((prev) => Math.min(presentationSlides.length - 1, prev + 1))}
              className="px-4 py-2 rounded-lg bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-xs font-bold"
            >
              Next Slide
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

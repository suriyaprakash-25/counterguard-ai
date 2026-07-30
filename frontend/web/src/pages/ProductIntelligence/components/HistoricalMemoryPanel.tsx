/**
 * HistoricalMemoryPanel.tsx — Organizational Memory Panel
 * Displays vector similarity investigation precedents, historical verdicts, and recommendations.
 */
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Database, Sparkles, Clock, ExternalLink, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { apiClient, endpoints } from '../../../shared/api';

interface MemoryMatchItem {
  id: string;
  title: string;
  category: string;
  similarity_pct: number;
  verdict: string;
  marketplace?: string;
  seller?: string;
  summary: string;
}

interface MemorySearchResponse {
  query: string;
  total_matches: number;
  matches: MemoryMatchItem[];
  recommendation: string;
}

interface HistoricalMemoryPanelProps {
  query: string;
}

export function HistoricalMemoryPanel({ query }: HistoricalMemoryPanelProps) {
  const searchQuery = query || 'CMF Buds';

  const { data, isLoading } = useQuery<MemorySearchResponse>({
    queryKey: ['memory', 'similar', searchQuery],
    queryFn: async () => {
      const resp = await apiClient.get(`${endpoints.memory.similarInvestigations}?query=${encodeURIComponent(searchQuery)}`);
      return resp.data;
    },
  });

  if (isLoading || !data) return null;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3 mb-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Database className="h-4 w-4 text-violet-600 dark:text-violet-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            Organizational Vector Memory Precedents
          </h3>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{data.total_matches} Matching Precedents</span>
      </div>

      {/* Recommendation Banner */}
      {data.recommendation && (
        <div className="p-3 rounded-lg bg-violet-50 dark:bg-violet-950/40 border border-violet-200 dark:border-violet-800 text-xs text-violet-900 dark:text-violet-200 font-medium flex items-start gap-2">
          <Sparkles className="h-4 w-4 text-violet-600 dark:text-violet-400 shrink-0 mt-0.5" />
          <span>{data.recommendation}</span>
        </div>
      )}

      {/* Precedent Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {data.matches.slice(0, 2).map((item) => {
          const isCrit = item.verdict === 'CRITICAL';
          const isHigh = item.verdict === 'HIGH';

          return (
            <div
              key={item.id}
              className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-2 text-xs"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="font-bold text-slate-900 dark:text-white truncate" title={item.title}>
                  {item.title}
                </div>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300 shrink-0">
                  {item.similarity_pct}% Match
                </span>
              </div>

              <p className="text-[11px] text-slate-600 dark:text-slate-400 line-clamp-2">{item.summary}</p>

              <div className="flex items-center justify-between text-[10px] text-slate-500 pt-1 border-t border-slate-200 dark:border-slate-700">
                <span>{item.marketplace} • {item.seller}</span>
                <span className={`font-bold ${isCrit ? 'text-red-600' : isHigh ? 'text-amber-600' : 'text-emerald-600'}`}>
                  Verdict: {item.verdict}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

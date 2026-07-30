/**
 * HighRiskSellersWidget.tsx — High Risk Seller Directory Widget
 * Displays known high-risk merchants, marketplaces, GSTINs, and risk scores.
 */
import React from 'react';
import { Users, AlertTriangle, ExternalLink, ShieldAlert } from 'lucide-react';

export interface SellerRecord {
  id: string;
  name: string;
  marketplace: string;
  risk_score: number;
  location?: string;
  gstin?: string;
  investigations_count: number;
}

interface HighRiskSellersWidgetProps {
  sellers?: SellerRecord[];
}

const DEFAULT_SELLERS: SellerRecord[] = [
  { id: 's1', name: 'Shenzhen Precision Mfg', marketplace: 'TradeIndia', risk_score: 94, location: 'Shenzhen, CN', gstin: '99BBBBB1111B2Z3', investigations_count: 5 },
  { id: 's2', name: 'Fashion Hub Wholesale', marketplace: 'Meesho', risk_score: 90, location: 'Surat, GJ', gstin: '07AAAAA0000A1Z5', investigations_count: 4 },
  { id: 's3', name: 'Radha Wholesale Enterprise', marketplace: 'Meesho', risk_score: 88, location: 'Surat, GJ', gstin: '07AAAAA0000A1Z5', investigations_count: 6 },
  { id: 's4', name: 'Global ElectroDeals', marketplace: 'Amazon', risk_score: 78, location: 'Delhi NCR', gstin: '07CCCCCC2222C3Z4', investigations_count: 3 },
];

export function HighRiskSellersWidget({ sellers = DEFAULT_SELLERS }: HighRiskSellersWidgetProps) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-red-600 dark:text-red-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            High Risk Merchant Entities
          </h3>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{sellers.length} High Risk Merchants</span>
      </div>

      <div className="space-y-2">
        {sellers.map((s) => (
          <div
            key={s.id}
            className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-xs flex items-center justify-between gap-3"
          >
            <div className="space-y-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-900 dark:text-white truncate">{s.name}</span>
                <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                  {s.marketplace}
                </span>
              </div>
              <div className="text-[10px] text-slate-500 flex items-center gap-3">
                {s.location && <span>📍 {s.location}</span>}
                {s.gstin && <span className="font-mono">GST: {s.gstin}</span>}
              </div>
            </div>

            <div className="text-right shrink-0">
              <div className="text-sm font-bold text-red-600 dark:text-red-400">{s.risk_score}/100</div>
              <div className="text-[10px] text-slate-400">{s.investigations_count} Cases</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

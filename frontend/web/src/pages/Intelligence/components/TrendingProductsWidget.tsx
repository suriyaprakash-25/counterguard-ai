/**
 * TrendingProductsWidget.tsx — Trending Counterfeit Target Products Watchlist
 * Displays target products, price spread, counterfeit detection rate, and risk status.
 */
import React from 'react';
import { Sparkles, AlertTriangle, TrendingUp, Layers } from 'lucide-react';

export interface ProductWatchItem {
  id: string;
  name: string;
  category: string;
  price_spread: string;
  risk_score: number;
  replica_detection_pct: number;
}

const DEFAULT_PRODUCTS: ProductWatchItem[] = [
  { id: 'p1', name: 'CMF Buds 2a', category: 'Audio / Wireless', price_spread: '₹799 – ₹2,499', risk_score: 85, replica_detection_pct: 72 },
  { id: 'p2', name: 'Sony WH-1000XM5', category: 'Audio / ANC Headphones', price_spread: '₹2,999 – ₹29,990', risk_score: 74, replica_detection_pct: 45 },
  { id: 'p3', name: 'Nothing Phone 3 Charger', category: 'Mobile Accessories', price_spread: '₹399 – ₹2,499', risk_score: 90, replica_detection_pct: 88 },
  { id: 'p4', name: 'Nike C1TY Sneakers', category: 'Footwear', price_spread: '₹1,499 – ₹8,995', risk_score: 65, replica_detection_pct: 35 },
];

export function TrendingProductsWidget({ products = DEFAULT_PRODUCTS }: { products?: ProductWatchItem[] }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-violet-600 dark:text-violet-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            Target Counterfeit Product Watchlist
          </h3>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{products.length} Products Monitored</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {products.map((p) => (
          <div
            key={p.id}
            className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-2 text-xs"
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <div className="font-bold text-slate-900 dark:text-white">{p.name}</div>
                <div className="text-[10px] text-slate-500">{p.category}</div>
              </div>
              <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300">
                {p.replica_detection_pct}% Fake Rate
              </span>
            </div>

            <div className="flex items-center justify-between text-[11px] pt-1 border-t border-slate-200 dark:border-slate-700">
              <span className="text-slate-500 font-mono">Price: {p.price_spread}</span>
              <span className="font-bold text-red-600 dark:text-red-400">Threat: {p.risk_score}/100</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * ProductSearchBar.tsx — Refactored to light theme design system
 * Light, crisp input with marketplace chips and primary violet discovery action.
 */
import React, { useRef, useEffect } from 'react';
import { Search, Loader2, X, Filter, Sparkles } from 'lucide-react';

const MARKETPLACE_CHIPS: Record<string, { active: string; inactive: string }> = {
  Amazon:     { active: 'bg-amber-100 text-amber-900 border-amber-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' },
  Flipkart:   { active: 'bg-blue-100 text-blue-900 border-blue-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' },
  Meesho:     { active: 'bg-pink-100 text-pink-900 border-pink-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' },
  TradeIndia: { active: 'bg-emerald-100 text-emerald-900 border-emerald-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' },
  AJIO:       { active: 'bg-purple-100 text-purple-900 border-purple-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' },
  Myntra:     { active: 'bg-rose-100 text-rose-900 border-rose-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' },
};

interface ProductSearchBarProps {
  query: string;
  onQueryChange: (q: string) => void;
  onSearch: () => void;
  isSearching: boolean;
  supportedMarketplaces: string[];
  activeMarketplaces: Set<string>;
  onToggleMarketplace: (mp: string) => void;
  onClearMarketplaces: () => void;
  suggestions?: string[];
}

export function ProductSearchBar({
  query,
  onQueryChange,
  onSearch,
  isSearching,
  supportedMarketplaces,
  activeMarketplaces,
  onToggleMarketplace,
  onClearMarketplaces,
  suggestions = ['CMF Buds 2a', 'Sony WH-1000XM5', 'boAt Airdopes 141', 'Nike Air Max 270', 'Samsung Galaxy S24'],
}: ProductSearchBarProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && query.trim() && !isSearching) onSearch();
  };

  return (
    <div className="relative">
      {/* Hero search input box */}
      <div className="relative flex items-center gap-3">
        <div className="relative flex-1">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-2 pointer-events-none">
            {isSearching
              ? <Loader2 className="h-5 w-5 text-violet-600 animate-spin" />
              : <Search className="h-5 w-5 text-slate-400" />
            }
          </div>
          <input
            ref={inputRef}
            id="product-search-input"
            type="text"
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='Search any product e.g. "Nothing Charger", "Sony WH-1000XM5"…'
            className="w-full pl-12 pr-10 py-3.5 rounded-xl bg-white border border-slate-200 text-slate-900 text-base placeholder-slate-400 outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 transition-all shadow-sm"
          />
          {query && (
            <button
              onClick={() => onQueryChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-700 transition-colors"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
        <button
          id="product-search-btn"
          onClick={onSearch}
          disabled={isSearching || !query.trim()}
          className="px-6 py-3.5 rounded-xl bg-violet-600 hover:bg-violet-700 active:bg-violet-800 disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold text-sm transition-all shadow-sm flex items-center gap-2 shrink-0"
        >
          {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {isSearching ? 'Searching…' : 'Discover'}
        </button>
      </div>

      {/* Quick suggestions */}
      {!query && (
        <div className="mt-3 flex flex-wrap gap-2 items-center">
          <span className="text-xs text-slate-500 font-medium flex items-center gap-1 mr-1">
            <Search className="h-3 w-3" /> Try searching:
          </span>
          {suggestions.map((s) => (
            <button
              key={s}
              onClick={() => { onQueryChange(s); setTimeout(onSearch, 50); }}
              className="px-3 py-1 rounded-full text-xs font-medium bg-slate-100 border border-slate-200 text-slate-700 hover:bg-violet-50 hover:text-violet-700 hover:border-violet-300 transition-all"
            >
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Marketplace filter chips */}
      <div className="mt-3 flex items-center gap-2 flex-wrap">
        <span className="flex items-center gap-1 text-xs font-semibold text-slate-500 uppercase tracking-wider shrink-0">
          <Filter className="h-3 w-3" /> Filter Markets:
        </span>
        {supportedMarketplaces.map((mp) => {
          const active = activeMarketplaces.has(mp);
          const chipStyle = MARKETPLACE_CHIPS[mp] ?? { active: 'bg-violet-100 text-violet-900 border-violet-300 font-semibold', inactive: 'bg-slate-100 text-slate-600 border-slate-200 hover:bg-slate-200/70 hover:text-slate-900' };
          return (
            <button
              key={mp}
              id={`filter-mp-${mp.toLowerCase()}`}
              onClick={() => onToggleMarketplace(mp)}
              className={`px-3 py-1 rounded-full text-xs border transition-all duration-150 ${
                active ? chipStyle.active : chipStyle.inactive
              }`}
            >
              {mp}
            </button>
          );
        })}
        {activeMarketplaces.size > 0 && (
          <button
            onClick={onClearMarketplaces}
            className="px-2 py-1 text-xs text-slate-500 hover:text-slate-800 transition-colors flex items-center gap-1 font-medium"
          >
            <X className="h-3 w-3" /> Clear filters
          </button>
        )}
      </div>
    </div>
  );
}

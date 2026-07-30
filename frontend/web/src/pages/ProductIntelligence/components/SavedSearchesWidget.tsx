/**
 * SavedSearchesWidget.tsx — Phase 7 & 8: Saved Searches & Bookmarked Investigations Widget
 * Allows investigators to quick-launch saved search profiles, pin target products, and bookmark cases.
 */
import React, { useState } from 'react';
import { Bookmark, Star, Pin, Search, Plus, Trash2 } from 'lucide-react';

interface SavedSearchItem {
  id: string;
  name: string;
  query: string;
  isPinned?: boolean;
}

interface SavedSearchesWidgetProps {
  onSelectQuery: (query: string) => void;
}

const DEFAULT_SAVED_SEARCHES: SavedSearchItem[] = [
  { id: 's1', name: 'CMF Buds 2a', query: 'CMF Buds 2a', isPinned: true },
  { id: 's2', name: 'Sony WH-1000XM5', query: 'Sony WH-1000XM5', isPinned: true },
  { id: 's3', name: 'Nothing Phone 3', query: 'Nothing Phone 3', isPinned: false },
  { id: 's4', name: 'Nike C1TY Sneakers', query: 'Nike C1TY', isPinned: false },
];

export function SavedSearchesWidget({ onSelectQuery }: SavedSearchesWidgetProps) {
  const [items, setItems] = useState<SavedSearchItem[]>(DEFAULT_SAVED_SEARCHES);

  const togglePin = (id: string) => {
    setItems((prev) =>
      prev.map((item) => (item.id === id ? { ...item, isPinned: !item.isPinned } : item))
    );
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3 mb-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Bookmark className="h-4 w-4 text-violet-600 dark:text-violet-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            Saved Searches & Pinned Products
          </h3>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{items.length} Saved Profiles</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <div
            key={item.id}
            className="group flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-xs font-medium text-slate-800 dark:text-slate-200 hover:border-violet-300 dark:hover:border-violet-500 transition-all"
          >
            <button
              onClick={() => onSelectQuery(item.query)}
              className="flex items-center gap-1.5 hover:text-violet-600 dark:hover:text-violet-400 transition-colors"
            >
              <Search className="h-3.5 w-3.5 text-slate-400" />
              <span>{item.name}</span>
            </button>
            <button
              onClick={() => togglePin(item.id)}
              className={`p-0.5 rounded text-slate-400 hover:text-amber-500 transition-colors ${
                item.isPinned ? 'text-amber-500' : ''
              }`}
              title="Pin search"
            >
              <Pin className="h-3 w-3" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

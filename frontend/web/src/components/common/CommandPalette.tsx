/**
 * CommandPalette.tsx — Phase 11: Enterprise Command Palette (Ctrl+K / Cmd+K)
 * Instant global search across products, marketplaces, pages, and enterprise SOC actions.
 */
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Command,
  Sparkles,
  Shield,
  Layers,
  BarChart3,
  Settings,
  FileText,
  Moon,
  Sun,
  X,
  ArrowRight,
} from 'lucide-react';
import { useDarkMode } from '../../context/DarkModeContext';

interface CommandItem {
  id: string;
  category: 'Products' | 'Pages' | 'Actions';
  title: string;
  subtitle?: string;
  icon: React.ElementType;
  action: () => void;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectProductQuery?: (query: string) => void;
}

export function CommandPalette({ isOpen, onClose, onSelectProductQuery }: CommandPaletteProps) {
  const navigate = useNavigate();
  const { darkMode, toggleDarkMode } = useDarkMode();
  const [search, setSearch] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else {
          // Open triggered by parent state or keyboard event
        }
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const items: CommandItem[] = [
    // Products
    {
      id: 'cmd-p-nothing',
      category: 'Products',
      title: 'Nothing Charger 45W',
      subtitle: 'Fast discovery & counterfeit scan',
      icon: Sparkles,
      action: () => {
        onSelectProductQuery?.('Nothing Charger');
        navigate('/product-intelligence');
        onClose();
      },
    },
    {
      id: 'cmd-p-cmf',
      category: 'Products',
      title: 'CMF Buds 2a',
      subtitle: 'Wireless Earbuds multi-marketplace audit',
      icon: Sparkles,
      action: () => {
        onSelectProductQuery?.('CMF Buds 2a');
        navigate('/product-intelligence');
        onClose();
      },
    },
    {
      id: 'cmd-p-sony',
      category: 'Products',
      title: 'Sony WH-1000XM5',
      subtitle: 'Noise Cancelling Headphones verification',
      icon: Sparkles,
      action: () => {
        onSelectProductQuery?.('Sony WH-1000XM5');
        navigate('/product-intelligence');
        onClose();
      },
    },
    {
      id: 'cmd-p-nike',
      category: 'Products',
      title: 'Nike C1TY Sneakers',
      subtitle: 'Footwear replica & seller audit',
      icon: Sparkles,
      action: () => {
        onSelectProductQuery?.('Nike C1TY');
        navigate('/product-intelligence');
        onClose();
      },
    },

    // Pages
    {
      id: 'cmd-page-disc',
      category: 'Pages',
      title: 'Product Intelligence Command Center',
      subtitle: 'Multi-marketplace discovery workspace',
      icon: Sparkles,
      action: () => {
        navigate('/product-intelligence');
        onClose();
      },
    },
    {
      id: 'cmd-page-inv',
      category: 'Pages',
      title: 'Investigations Operations',
      subtitle: 'Active swarm case files & verdicts',
      icon: Layers,
      action: () => {
        navigate('/investigations');
        onClose();
      },
    },
    {
      id: 'cmd-page-analytics',
      category: 'Pages',
      title: 'Analytics & Threat Telemetry',
      subtitle: 'Marketplace risk metrics & agent execution',
      icon: BarChart3,
      action: () => {
        navigate('/analytics');
        onClose();
      },
    },

    // Actions
    {
      id: 'cmd-act-theme',
      category: 'Actions',
      title: darkMode ? 'Switch to Light Theme' : 'Switch to Enterprise SOC Dark Mode',
      subtitle: 'Toggle SOC visual theme',
      icon: darkMode ? Sun : Moon,
      action: () => {
        toggleDarkMode();
        onClose();
      },
    },
  ];

  const filteredItems = items.filter(
    (i) =>
      i.title.toLowerCase().includes(search.toLowerCase()) ||
      (i.subtitle && i.subtitle.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 backdrop-blur-sm flex items-start justify-center pt-24 p-4">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl w-full max-w-xl overflow-hidden flex flex-col text-slate-900 dark:text-white animate-in zoom-in-95 duration-150">
        {/* Input header */}
        <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-3">
          <Search className="h-5 w-5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Type a command or product name… (Esc to close)"
            className="w-full bg-transparent text-sm placeholder-slate-400 outline-none"
            autoFocus
          />
          <button onClick={onClose} className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Command list */}
        <div className="max-h-96 overflow-y-auto p-2 divide-y divide-slate-100 dark:divide-slate-800">
          {filteredItems.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">No matching commands or products found</div>
          ) : (
            filteredItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={item.action}
                  className="w-full p-3 rounded-xl hover:bg-violet-50 dark:hover:bg-slate-800 transition-colors flex items-center justify-between text-left group"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 group-hover:bg-violet-600 group-hover:text-white transition-colors">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-slate-900 dark:text-white">{item.title}</div>
                      {item.subtitle && <div className="text-[11px] text-slate-500 dark:text-slate-400">{item.subtitle}</div>}
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              );
            })
          )}
        </div>

        {/* Footer */}
        <div className="p-3 bg-slate-50 dark:bg-slate-800/60 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-500 dark:text-slate-400 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-700 font-mono text-[10px]">Ctrl+K</kbd>
            <span>Quick Palette</span>
          </div>
          <div>CounterGuard Enterprise SOC</div>
        </div>
      </div>
    </div>
  );
}

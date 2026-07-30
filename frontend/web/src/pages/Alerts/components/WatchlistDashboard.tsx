/**
 * WatchlistDashboard.tsx — Phase 4: Watchlist Manager Dashboard Component
 * Manages 8 target entity categories (Brands, Products, Sellers, Phones, Emails, GST Numbers, Fraud Rings, Marketplaces).
 */
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Pause, Play, Trash2, Download, Shield, Eye, Tag, FileText, Clock } from 'lucide-react';
import { apiClient, endpoints } from '../../../shared/api';

export interface WatchlistItem {
  id: string;
  category: string;
  value: string;
  name: string;
  status: 'ACTIVE' | 'PAUSED';
  created_at: string;
  next_run?: string;
  alert_count: number;
}

function WatchlistCountdown({ nextRun }: { nextRun?: string }) {
  const [secondsLeft, setSecondsLeft] = useState<number | null>(() => {
    if (!nextRun) return null;
    const targetMs = new Date(nextRun).getTime();
    if (isNaN(targetMs)) return null;
    return Math.max(0, Math.floor((targetMs - Date.now()) / 1000));
  });

  React.useEffect(() => {
    if (!nextRun) return;
    const targetMs = new Date(nextRun).getTime();
    if (isNaN(targetMs)) return;

    const updateTimer = () => {
      const remaining = Math.max(0, Math.floor((targetMs - Date.now()) / 1000));
      setSecondsLeft(remaining);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    return () => clearInterval(interval);
  }, [nextRun]);

  if (secondsLeft === null) return null;

  const mins = Math.floor(secondsLeft / 60);
  const secs = secondsLeft % 60;
  const formattedTime = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;

  return (
    <span className="font-mono font-bold text-blue-600 dark:text-blue-400 text-[10px] flex items-center gap-1">
      <Clock className="h-3 w-3 text-blue-500 animate-pulse" />
      in {formattedTime}
    </span>
  );
}

export function WatchlistDashboard() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newCat, setNewCat] = useState('GST');
  const [newVal, setNewVal] = useState('');
  const [newName, setNewName] = useState('');

  const { data: watchlists = [], isLoading } = useQuery<WatchlistItem[]>({
    queryKey: ['watchlists'],
    queryFn: async () => {
      const resp = await apiClient.get(`${endpoints.watchlists.list}`);
      return resp.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post(`${endpoints.watchlists.create}`, {
        category: newCat,
        value: newVal,
        name: newName,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlists'] });
      setIsModalOpen(false);
      setNewVal('');
      setNewName('');
    },
  });

  const togglePauseMutation = useMutation({
    mutationFn: async ({ id, isPaused }: { id: string; isPaused: boolean }) => {
      const ep = isPaused ? endpoints.watchlists.resume(id) : endpoints.watchlists.pause(id);
      await apiClient.post(ep);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlists'] }),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(endpoints.watchlists.delete(id));
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['watchlists'] }),
  });

  const handleExportCSV = () => {
    window.open(`${apiClient.defaults.baseURL || ''}/api/v1/watchlists/export`, '_blank');
  };

  if (isLoading) return null;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            Watchlist Target Management Hub (8 Entity Categories)
          </h3>
          <p className="text-[11px] text-slate-500">Brands, Products, Sellers, Phones, Emails, GST Numbers, Fraud Rings, Marketplaces</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCSV}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 text-xs font-semibold flex items-center gap-1.5 hover:bg-slate-50 dark:hover:bg-slate-800"
          >
            <Download className="h-3.5 w-3.5" /> Export CSV
          </button>
          <button
            onClick={() => setIsModalOpen(true)}
            className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold flex items-center gap-1.5"
          >
            <Plus className="h-3.5 w-3.5" /> Add Target
          </button>
        </div>
      </div>

      {/* Target Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {watchlists.map((item) => {
          const isPaused = item.status === 'PAUSED';

          return (
            <div
              key={item.id}
              className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-2 text-xs flex flex-col justify-between"
            >
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300 uppercase tracking-wider">
                    {item.category}
                  </span>
                  <span className={`text-[10px] font-bold ${isPaused ? 'text-amber-600' : 'text-emerald-600'}`}>
                    {item.status}
                  </span>
                </div>
                <div className="font-bold text-slate-900 dark:text-white truncate" title={item.name}>
                  {item.name}
                </div>
                <div className="text-[10px] font-mono text-slate-500 truncate" title={item.value}>
                  {item.value}
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-slate-200 dark:border-slate-700">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-slate-400">{item.alert_count} Alerts</span>
                  {!isPaused && item.next_run && <WatchlistCountdown nextRun={item.next_run} />}
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => togglePauseMutation.mutate({ id: item.id, isPaused })}
                    className="p-1 rounded hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300"
                    title={isPaused ? 'Resume' : 'Pause'}
                  >
                    {isPaused ? <Play className="h-3.5 w-3.5" /> : <Pause className="h-3.5 w-3.5" />}
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(item.id)}
                    className="p-1 rounded hover:bg-red-100 dark:hover:bg-red-950 text-red-600"
                    title="Delete Target"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Add Target Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              Add Watchlist Surveillance Target
            </h3>

            <div className="space-y-3 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Target Category</label>
                <select
                  value={newCat}
                  onChange={(e) => setNewCat(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 outline-none"
                >
                  <option value="GST">GST Number</option>
                  <option value="BRAND">Brand Target</option>
                  <option value="PRODUCT">Product SKU</option>
                  <option value="SELLER">Seller Handle</option>
                  <option value="PHONE">Phone Number</option>
                  <option value="EMAIL">Email Address</option>
                  <option value="FRAUD_RING">Fraud Ring Cluster</option>
                  <option value="MARKETPLACE">Marketplace Channel</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Target Title</label>
                <input
                  type="text"
                  placeholder="e.g. Surat Tax Registration Watch"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 outline-none"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 dark:text-slate-300 mb-1">Target Query / Value</label>
                <input
                  type="text"
                  placeholder="e.g. 07AAAAA0000A1Z5 or +91 98765-43210"
                  value={newVal}
                  onChange={(e) => setNewVal(e.target.value)}
                  className="w-full h-9 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 outline-none"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 text-xs font-semibold"
              >
                Cancel
              </button>
              <button
                onClick={() => createMutation.mutate()}
                className="px-3 py-1.5 rounded-lg bg-violet-600 text-white text-xs font-semibold"
              >
                Add Target
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

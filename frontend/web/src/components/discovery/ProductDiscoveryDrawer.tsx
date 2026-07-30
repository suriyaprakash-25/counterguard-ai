import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  Search,
  X,
  Loader2,
  ExternalLink,
  ShieldCheck,
  ShieldAlert,
  AlertCircle,
  Sparkles,
  Store,
  Tag,
  User,
  ChevronRight,
  Filter,
  RefreshCw,
  Globe,
} from 'lucide-react';
import { useProductDiscovery, useSupportedMarketplaces, useLaunchInvestigations, useBatchStatus } from '../../hooks/useDiscovery';
import type { ListingCandidate, ListingGroup } from '../../types/discovery';
import { getConfidenceTier, formatConfidence, getPriorityColor, formatPriorityScore, candidateToLaunchItem } from '../../types/discovery';
import { Layers, TrendingUp, Target, Rocket, CheckSquare, Square, X as XIcon } from 'lucide-react';

// ─── Marketplace brand colours ───────────────────────────────────────────────
const MARKETPLACE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  Amazon: { bg: 'bg-amber-500/20', text: 'text-amber-300', border: 'border-amber-500/40' },
  Flipkart: { bg: 'bg-blue-500/20', text: 'text-blue-300', border: 'border-blue-500/40' },
  Meesho: { bg: 'bg-pink-500/20', text: 'text-pink-300', border: 'border-pink-500/40' },
  TradeIndia: { bg: 'bg-green-500/20', text: 'text-green-300', border: 'border-green-500/40' },
  AJIO: { bg: 'bg-purple-500/20', text: 'text-purple-300', border: 'border-purple-500/40' },
  Myntra: { bg: 'bg-rose-500/20', text: 'text-rose-300', border: 'border-rose-500/40' },
};

const CONFIDENCE_STYLES = {
  high: {
    icon: ShieldCheck,
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/15',
    border: 'border-emerald-500/30',
    label: 'High Confidence',
  },
  medium: {
    icon: AlertCircle,
    color: 'text-amber-400',
    bg: 'bg-amber-500/15',
    border: 'border-amber-500/30',
    label: 'Medium Confidence',
  },
  low: {
    icon: ShieldAlert,
    color: 'text-red-400',
    bg: 'bg-red-500/15',
    border: 'border-red-500/30',
    label: 'Low Confidence',
  },
};

// ─── Sub-components ──────────────────────────────────────────────────────────

interface MarketplaceBadgeProps {
  name: string;
}

function MarketplaceBadge({ name }: MarketplaceBadgeProps) {
  const style = MARKETPLACE_COLORS[name] ?? {
    bg: 'bg-slate-500/20',
    text: 'text-slate-300',
    border: 'border-slate-500/40',
  };
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold border ${style.bg} ${style.text} ${style.border}`}
    >
      <Store className="h-3 w-3" />
      {name}
    </span>
  );
}

interface CandidateCardProps {
  candidate: ListingCandidate;
  onInvestigate: (candidate: ListingCandidate) => void;
}

function CandidateCard({ candidate, onInvestigate }: CandidateCardProps) {
  const tier = getConfidenceTier(candidate.confidence);
  const style = CONFIDENCE_STYLES[tier];
  const ConfIcon = style.icon;

  const displayPrice =
    candidate.price > 0
      ? `${candidate.currency === 'USD' ? '$' : '₹'}${candidate.price.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
      : 'Price not listed';

  return (
    <div className="group relative rounded-xl border border-slate-700/60 bg-slate-800/60 hover:bg-slate-800/90 hover:border-slate-600/80 transition-all duration-200 overflow-hidden">
      {/* Confidence accent strip */}
      <div
        className={`absolute inset-y-0 left-0 w-1 ${
          tier === 'high' ? 'bg-emerald-500' : tier === 'medium' ? 'bg-amber-500' : 'bg-red-500'
        }`}
      />

      <div className="p-4 pl-5">
        <div className="flex gap-3">
          {/* Thumbnail */}
          <div className="shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-slate-700/60 border border-slate-600/40">
            {candidate.thumbnail ? (
              <img
                src={candidate.thumbnail}
                alt={candidate.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Globe className="h-6 w-6 text-slate-500" />
              </div>
            )}
          </div>

          {/* Content */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2 mb-1.5">
              <p className="text-sm font-semibold text-white line-clamp-2 leading-snug">
                {candidate.title}
              </p>
              <MarketplaceBadge name={candidate.marketplace} />
            </div>

            {/* Price & Seller Row */}
            <div className="flex items-center gap-3 mb-2 flex-wrap">
              <span className="inline-flex items-center gap-1 text-sm font-bold text-cyan-300">
                <Tag className="h-3 w-3" />
                {displayPrice}
              </span>
              <span className="inline-flex items-center gap-1 text-xs text-slate-400">
                <User className="h-3 w-3" />
                <span className="truncate max-w-[160px]">{candidate.seller}</span>
              </span>
            </div>

            {/* Availability & Confidence row */}
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 italic">{candidate.availability}</span>
                <span
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border ${style.bg} ${style.color} ${style.border}`}
                >
                  <ConfIcon className="h-3 w-3" />
                  {formatConfidence(candidate.confidence)}
                </span>
              </div>

              {/* Action buttons */}
              <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-150">
                <a
                  href={candidate.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  id={`view-listing-${candidate.id}`}
                  className="inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium bg-slate-700/80 text-slate-300 hover:bg-slate-600 hover:text-white transition-colors border border-slate-600/50"
                  title="Open listing in new tab"
                >
                  <ExternalLink className="h-3 w-3" />
                  View
                </a>
                <button
                  id={`investigate-${candidate.id}`}
                  onClick={() => onInvestigate(candidate)}
                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors shadow-sm"
                >
                  Investigate
                  <ChevronRight className="h-3 w-3" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Source tag */}
        <div className="mt-2 pt-2 border-t border-slate-700/40">
          <span className="text-[11px] text-slate-500">
            Source: {candidate.discovery_source}
          </span>
        </div>
      </div>
    </div>
  );
}

// ─── Listing Group Card (Sprint 2.2) ─────────────────────────────────────────

interface ListingGroupCardProps {
  group: ListingGroup;
  onInvestigate: (candidate: ListingCandidate) => void;
}

function ListingGroupCard({ group, onInvestigate }: ListingGroupCardProps) {
  const [expanded, setExpanded] = useState(false);
  const ps = group.priority_score;
  const priorityStyle = getPriorityColor(group.investigation_priority);
  const priorityScore = ps ? ps.total_priority_score : 0;

  const priorityAccent =
    group.investigation_priority === 'critical' ? 'bg-red-500'
    : group.investigation_priority === 'high' ? 'bg-orange-500'
    : group.investigation_priority === 'normal' ? 'bg-blue-500'
    : 'bg-slate-500';

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/60 hover:bg-slate-800/90 transition-all duration-200 overflow-hidden">
      {/* Priority accent strip */}
      <div className={`h-1 w-full ${priorityAccent}`} />

      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold text-white line-clamp-2">{group.canonical_title}</p>
            <p className="text-xs text-slate-400 mt-0.5">{group.normalized_product_name}</p>
          </div>
          <span
            className={`shrink-0 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold border ${priorityStyle.bg} ${priorityStyle.text} ${priorityStyle.border}`}
          >
            {formatPriorityScore(priorityScore)}
          </span>
        </div>

        {/* Stats row */}
        <div className="flex flex-wrap gap-2 mb-2 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <Store className="h-3 w-3" />
            {group.listing_count} listing{group.listing_count !== 1 ? 's' : ''}
          </span>
          <span className="flex items-center gap-1">
            <Globe className="h-3 w-3" />
            {group.unique_marketplaces.join(', ')}
          </span>
          {group.price_range.min !== undefined && (
            <span className="flex items-center gap-1 text-cyan-400 font-medium">
              <Tag className="h-3 w-3" />
              ₹{group.price_range.min?.toLocaleString('en-IN', { maximumFractionDigits: 0 })} – ₹{group.price_range.max?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
            </span>
          )}
        </div>

        {/* Priority reasoning */}
        {ps && ps.reasoning.length > 0 && (
          <div className="mb-2 space-y-1">
            {ps.reasoning.slice(0, 2).map((r, i) => (
              <p key={i} className={`text-[11px] ${priorityStyle.text} flex items-start gap-1.5`}>
                <span className="mt-0.5 shrink-0">⚠</span>
                <span>{r}</span>
              </p>
            ))}
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-slate-400 hover:text-violet-300 transition-colors flex items-center gap-1"
          >
            <ChevronRight className={`h-3 w-3 transition-transform ${expanded ? 'rotate-90' : ''}`} />
            {expanded ? 'Hide' : 'Show'} {group.listing_count} listings
          </button>
          {group.representative && (
            <button
              id={`investigate-group-${group.group_id}`}
              onClick={() => onInvestigate(group.representative!)}
              className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white transition-colors shadow-sm"
            >
              Investigate Best
              <ChevronRight className="h-3 w-3" />
            </button>
          )}
        </div>

        {/* Expanded listings */}
        {expanded && (
          <div className="mt-3 space-y-2 border-t border-slate-700/40 pt-3">
            {group.listings.map((listing) => (
              <div key={listing.id} className="flex items-center justify-between gap-2 py-1">
                <div className="flex-1 min-w-0">
                  <p className="text-xs text-slate-300 truncate">{listing.marketplace} — {listing.seller}</p>
                  <p className="text-xs text-cyan-300 font-medium">
                    {listing.price > 0 ? `₹${listing.price.toLocaleString('en-IN', { maximumFractionDigits: 0 })}` : 'N/A'}
                  </p>
                </div>
                <button
                  onClick={() => onInvestigate(listing)}
                  className="shrink-0 text-xs text-violet-400 hover:text-violet-300 font-semibold flex items-center gap-0.5"
                >
                  Investigate <ChevronRight className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Main Drawer ─────────────────────────────────────────────────────────────

interface ProductDiscoveryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  /** Called when user clicks "Investigate" on a candidate — receives the listing URL */
  onInvestigateUrl: (url: string, title: string) => void;
}

type DrawerTab = 'targets' | 'groups' | 'all';

export function ProductDiscoveryDrawer({
  isOpen,
  onClose,
  onInvestigateUrl,
}: ProductDiscoveryDrawerProps) {
  const [query, setQuery] = useState('');
  const [activeMarketplaces, setActiveMarketplaces] = useState<Set<string>>(new Set());
  const [lastSearchedQuery, setLastSearchedQuery] = useState('');
  const [activeTab, setActiveTab] = useState<DrawerTab>('targets');

  const inputRef = useRef<HTMLInputElement>(null);

  const { data: marketplacesData } = useSupportedMarketplaces();
  const supportedMarketplaces = marketplacesData?.supported_marketplaces ?? [
    'Amazon',
    'Flipkart',
    'Meesho',
    'TradeIndia',
    'AJIO',
    'Myntra',
  ];

  const {
    mutate: searchProducts,
    data: searchResult,
    isPending: isSearching,
    reset: resetSearch,
    isError,
    error,
  } = useProductDiscovery();

  // Auto-focus input on open
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
    if (!isOpen) {
      setQuery('');
      setLastSearchedQuery('');
      setActiveMarketplaces(new Set());
      resetSearch();
    }
  }, [isOpen, resetSearch]);

  const handleSearch = useCallback(() => {
    if (!query.trim() || isSearching) return;
    setLastSearchedQuery(query.trim());
    searchProducts({
      query: query.trim(),
      marketplaces: activeMarketplaces.size > 0 ? Array.from(activeMarketplaces) : undefined,
      limit_per_marketplace: 3,
    });
  }, [query, isSearching, activeMarketplaces, searchProducts]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') handleSearch();
    if (e.key === 'Escape') onClose();
  };

  const toggleMarketplace = (marketplace: string) => {
    setActiveMarketplaces((prev) => {
      const next = new Set(prev);
      if (next.has(marketplace)) {
        next.delete(marketplace);
      } else {
        next.add(marketplace);
      }
      return next;
    });
  };

  const { mutate: launchBatch, data: launchResult, isPending: isLaunching, reset: resetLaunch } = useLaunchInvestigations();
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null);
  const { data: batchStatus } = useBatchStatus(activeBatchId);

  // Multi-select for batch launch
  const [selectedCandidateIds, setSelectedCandidateIds] = useState<Set<string>>(new Set());

  const toggleCandidateSelection = (candidateId: string) => {
    setSelectedCandidateIds((prev) => {
      const next = new Set(prev);
      if (next.has(candidateId)) next.delete(candidateId);
      else if (next.size < 10) next.add(candidateId);
      return next;
    });
  };

  const handleBatchLaunch = () => {
    const selectedCandidates = candidates.filter((c) => selectedCandidateIds.has(c.id));
    if (selectedCandidates.length === 0) return;
    launchBatch(
      {
        candidates: selectedCandidates.map(candidateToLaunchItem),
        investigation_type: 'Counterfeit Detection',
        planner_strategy: 'Balanced Investigation',
        priority: 'high',
      },
      {
        onSuccess: (data) => {
          setActiveBatchId(data.batch_id);
          setSelectedCandidateIds(new Set());
        },
      }
    );
  };

  const handleSingleInvestigate = (candidate: ListingCandidate) => {
    onInvestigateUrl(candidate.url, candidate.title);
    onClose();
  };

  const candidates = searchResult?.candidates ?? [];
  const listingGroups = searchResult?.listing_groups ?? [];
  const topTargets = searchResult?.top_investigation_targets ?? [];
  const hasResults = candidates.length > 0;

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer panel */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Product Discovery Search"
        className="fixed inset-y-0 right-0 z-50 flex flex-col w-full max-w-xl bg-slate-900 border-l border-slate-700/60 shadow-2xl"
        style={{ animation: 'slideInRight 0.22s ease-out' }}
      >
        {/* ── Header ────────────────────────────────────────────────── */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-slate-700/60 bg-slate-900/95">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-violet-500/20 border border-violet-500/40 flex items-center justify-center">
              <Sparkles className="h-4.5 w-4.5 text-violet-300" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Product Discovery</h2>
              <p className="text-xs text-slate-400">Search across all marketplaces instantly</p>
            </div>
          </div>
          <button
            id="discovery-drawer-close"
            onClick={onClose}
            className="h-8 w-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700/60 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* ── Search Bar ────────────────────────────────────────────── */}
        <div className="px-6 py-4 border-b border-slate-800/60 bg-slate-900/80">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
              <input
                ref={inputRef}
                id="discovery-search-input"
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder='e.g. "CMF Buds 2a", "Sony WH-1000XM5"'
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-800/80 border border-slate-600/60 text-white text-sm placeholder-slate-500 outline-none focus:border-violet-500/60 focus:ring-2 focus:ring-violet-500/20 transition-all"
              />
            </div>
            <button
              id="discovery-search-button"
              onClick={handleSearch}
              disabled={isSearching || !query.trim()}
              className="px-4 py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors flex items-center gap-2 shadow-sm"
            >
              {isSearching ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              {isSearching ? 'Searching…' : 'Search'}
            </button>
          </div>

          {/* Marketplace filters */}
          <div className="mt-3">
            <div className="flex items-center gap-1.5 mb-2">
              <Filter className="h-3 w-3 text-slate-500" />
              <span className="text-xs text-slate-500 font-medium">Filter by marketplace</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {supportedMarketplaces.map((mp) => {
                const active = activeMarketplaces.has(mp);
                const mpStyle = MARKETPLACE_COLORS[mp];
                return (
                  <button
                    key={mp}
                    id={`marketplace-filter-${mp.toLowerCase()}`}
                    onClick={() => toggleMarketplace(mp)}
                    className={`px-2.5 py-1 rounded-full text-xs font-semibold border transition-all duration-150 ${
                      active
                        ? `${mpStyle?.bg ?? 'bg-violet-500/20'} ${mpStyle?.text ?? 'text-violet-300'} ${mpStyle?.border ?? 'border-violet-500/40'} shadow-sm`
                        : 'bg-slate-800/60 text-slate-400 border-slate-700/60 hover:border-slate-600'
                    }`}
                  >
                    {mp}
                  </button>
                );
              })}
              {activeMarketplaces.size > 0 && (
                <button
                  onClick={() => setActiveMarketplaces(new Set())}
                  className="px-2.5 py-1 rounded-full text-xs font-semibold border border-slate-600/50 text-slate-400 hover:text-white hover:border-slate-500 transition-all flex items-center gap-1"
                >
                  <RefreshCw className="h-2.5 w-2.5" />
                  Clear
                </button>
              )}
            </div>
          </div>
        </div>

        {/* ── Results ───────────────────────────────────────────────── */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-3">
          {/* Idle state */}
          {!isSearching && !searchResult && !isError && (
            <div className="flex flex-col items-center justify-center h-72 gap-4 text-center">
              <div className="h-16 w-16 rounded-2xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                <Sparkles className="h-7 w-7 text-violet-400" />
              </div>
              <div>
                <p className="text-white font-semibold mb-1">Discover Product Listings</p>
                <p className="text-slate-400 text-sm max-w-xs">
                  Enter a product name to instantly scan <span className="text-violet-300 font-medium">{supportedMarketplaces.length} marketplaces</span> for candidate listings you can investigate.
                </p>
              </div>
              <div className="flex flex-wrap gap-2 justify-center text-xs text-slate-500">
                {['CMF Buds 2a', 'Sony WH-1000XM5', 'Nike Air Max', 'boAt Airdopes'].map((ex) => (
                  <button
                    key={ex}
                    onClick={() => setQuery(ex)}
                    className="px-3 py-1 rounded-full bg-slate-800 border border-slate-700 hover:border-violet-500/40 hover:text-violet-300 transition-all"
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Loading shimmer */}
          {isSearching && (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="rounded-xl border border-slate-700/40 bg-slate-800/40 p-4 animate-pulse">
                  <div className="flex gap-3">
                    <div className="w-16 h-16 rounded-lg bg-slate-700/60" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-slate-700/60 rounded w-3/4" />
                      <div className="h-3 bg-slate-700/40 rounded w-1/2" />
                      <div className="h-3 bg-slate-700/40 rounded w-1/3" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Error state */}
          {isError && (
            <div className="flex flex-col items-center justify-center h-48 gap-3">
              <ShieldAlert className="h-10 w-10 text-red-400" />
              <p className="text-red-300 font-medium text-sm">Discovery search failed</p>
              <p className="text-slate-400 text-xs text-center max-w-xs">
                {error?.message ?? 'An unexpected error occurred. Please try again.'}
              </p>
              <button
                onClick={handleSearch}
                className="px-4 py-2 rounded-lg bg-slate-700 text-white text-sm hover:bg-slate-600 transition-colors border border-slate-600"
              >
                Retry
              </button>
            </div>
          )}

          {/* Results */}
          {!isSearching && hasResults && (
            <>
              {/* Tab switcher */}
              <div className="flex items-center gap-1 mb-3 bg-slate-800/60 rounded-xl p-1 border border-slate-700/40">
                <button
                  id="tab-targets"
                  onClick={() => setActiveTab('targets')}
                  className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeTab === 'targets'
                      ? 'bg-violet-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Target className="h-3 w-3" />
                  Top Targets ({topTargets.length})
                </button>
                <button
                  id="tab-groups"
                  onClick={() => setActiveTab('groups')}
                  className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeTab === 'groups'
                      ? 'bg-violet-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <Layers className="h-3 w-3" />
                  Groups ({listingGroups.length})
                </button>
                <button
                  id="tab-all"
                  onClick={() => setActiveTab('all')}
                  className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeTab === 'all'
                      ? 'bg-violet-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <TrendingUp className="h-3 w-3" />
                  All ({candidates.length})
                </button>
              </div>

              {/* Result metadata */}
              <div className="flex items-center justify-between mb-2 text-xs text-slate-500">
                <span>
                  {lastSearchedQuery && (
                    <>Results for <span className="text-violet-300 font-medium">"{lastSearchedQuery}"</span> · </>
                  )}
                  {searchResult?.metadata?.deduplication_reduction} duplicates removed
                </span>
                <span>{searchResult?.metadata?.duration_ms}ms</span>
              </div>

              {/* Top Targets tab */}
              {activeTab === 'targets' && (
                <div className="space-y-3">
                  <p className="text-xs text-slate-400 pb-1">
                    Highest-risk listings selected for immediate investigation, one per product group.
                  </p>
                  {topTargets.map((candidate) => (
                    <CandidateCard
                      key={candidate.id}
                      candidate={candidate}
                      onInvestigate={handleSingleInvestigate}
                    />
                  ))}
                </div>
              )}

              {/* Ranked Groups tab */}
              {activeTab === 'groups' && (
                <div className="space-y-3">
                  <p className="text-xs text-slate-400 pb-1">
                    Deduplicated product groups ranked by investigation priority score.
                  </p>
                  {listingGroups.map((group) => (
                    <ListingGroupCard
                      key={group.group_id}
                      group={group}
                      onInvestigate={handleSingleInvestigate}
                    />
                  ))}
                </div>
              )}

              {/* All Candidates tab — with multi-select checkboxes */}
              {activeTab === 'all' && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-400 pb-1">
                    <span>Select candidates for parallel investigation (max 10)</span>
                    {selectedCandidateIds.size > 0 && (
                      <button
                        onClick={() => setSelectedCandidateIds(new Set())}
                        className="flex items-center gap-1 text-slate-500 hover:text-white transition-colors"
                      >
                        <XIcon className="h-3 w-3" />
                        Clear ({selectedCandidateIds.size})
                      </button>
                    )}
                  </div>
                  {candidates.map((candidate) => {
                    const isSelected = selectedCandidateIds.has(candidate.id);
                    return (
                      <div key={candidate.id} className="relative">
                        {/* Selection overlay */}
                        <button
                          id={`select-candidate-${candidate.id}`}
                          onClick={() => toggleCandidateSelection(candidate.id)}
                          className={`absolute top-2 left-2 z-10 p-0.5 rounded transition-all ${
                            isSelected ? 'text-violet-400' : 'text-slate-600 hover:text-slate-300'
                          }`}
                          title={isSelected ? 'Deselect' : 'Select for batch launch'}
                        >
                          {isSelected
                            ? <CheckSquare className="h-4 w-4" />
                            : <Square className="h-4 w-4" />
                          }
                        </button>
                        <div className={`pl-6 rounded-xl ring-1 transition-all ${isSelected ? 'ring-violet-500/50 bg-violet-500/5' : 'ring-transparent'}`}>
                          <CandidateCard
                            candidate={candidate}
                            onInvestigate={handleSingleInvestigate}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}

          {/* No results state */}
          {!isSearching && searchResult && !hasResults && (
            <div className="flex flex-col items-center justify-center h-48 gap-3 text-center">
              <Search className="h-10 w-10 text-slate-500" />
              <p className="text-slate-300 font-medium text-sm">No candidates found</p>
              <p className="text-slate-500 text-xs max-w-xs">
                Try a different search term or adjust marketplace filters.
              </p>
            </div>
          )}
        </div>

        {/* ── Batch Launch Panel (Sprint 2.3) ────────────────────────────── */}
        {(selectedCandidateIds.size > 0 || activeBatchId) && (
          <div className="px-6 py-3 border-t border-violet-700/40 bg-violet-950/40">
            {/* Launch button bar */}
            {selectedCandidateIds.size > 0 && !activeBatchId && (
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-white">
                    {selectedCandidateIds.size} candidate{selectedCandidateIds.size > 1 ? 's' : ''} selected
                  </p>
                  <p className="text-xs text-slate-400">Ready for parallel investigation</p>
                </div>
                <button
                  id="batch-launch-btn"
                  onClick={handleBatchLaunch}
                  disabled={isLaunching}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold transition-colors shadow-sm"
                >
                  {isLaunching ? (
                    <><Loader2 className="h-4 w-4 animate-spin" /> Launching…</>
                  ) : (
                    <><Rocket className="h-4 w-4" /> Launch Parallel</>
                  )}
                </button>
              </div>
            )}

            {/* Batch progress tracker */}
            {activeBatchId && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Rocket className="h-4 w-4 text-violet-400" />
                    <span className="text-sm font-semibold text-white">
                      Batch Launched
                    </span>
                    {batchStatus?.is_complete && (
                      <span className="text-xs text-emerald-400 font-semibold">✓ Complete</span>
                    )}
                  </div>
                  <button
                    onClick={() => { setActiveBatchId(null); resetLaunch(); }}
                    className="text-xs text-slate-400 hover:text-white transition-colors"
                  >
                    Dismiss
                  </button>
                </div>

                {/* Progress bar */}
                <div className="h-1.5 w-full rounded-full bg-slate-700/60 mb-2">
                  <div
                    className="h-full rounded-full bg-violet-500 transition-all duration-500"
                    style={{ width: `${batchStatus?.progress_pct ?? 0}%` }}
                  />
                </div>

                {/* Job status counts */}
                <div className="flex gap-3 text-xs">
                  <span className="text-emerald-400">✓ {batchStatus?.completed ?? 0} done</span>
                  <span className="text-blue-400">⟳ {batchStatus?.in_progress ?? 0} running</span>
                  <span className="text-slate-400">○ {batchStatus?.pending ?? 0} pending</span>
                  {(batchStatus?.failed ?? 0) > 0 && (
                    <span className="text-red-400">✗ {batchStatus?.failed} failed</span>
                  )}
                </div>

                {/* Investigation links */}
                {launchResult && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {launchResult.jobs.map((job) => (
                      <a
                        key={job.investigation_id}
                        href={`/investigations/${job.investigation_id}`}
                        className="text-xs px-2 py-0.5 rounded-full bg-slate-700/60 text-slate-300 hover:text-violet-300 hover:bg-slate-700 transition-colors truncate max-w-[140px]"
                        title={job.title}
                      >
                        {job.marketplace}
                      </a>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── Footer ────────────────────────────────────────────────── */}
        {hasResults && !isSearching && !selectedCandidateIds.size && !activeBatchId && (
          <div className="px-6 py-3 border-t border-slate-700/60 bg-slate-900/90">
            <p className="text-xs text-slate-500 text-center">
              Click <span className="font-semibold text-violet-300">Investigate</span> for single analysis ·{' '}
              Switch to <span className="font-semibold text-violet-300">All</span> tab to select multiple for
              {' '}<span className="text-emerald-400 font-semibold">parallel launch</span>
            </p>
          </div>
        )}
      </div>

      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0; }
          to { transform: translateX(0); opacity: 1; }
        }
      `}</style>
    </>
  );
}

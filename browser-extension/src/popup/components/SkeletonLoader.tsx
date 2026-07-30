/**
 * SkeletonLoader.tsx — Animated loading skeleton placeholders
 * Used while lazy-loaded popup tabs or async data is loading.
 * Respects prefers-reduced-motion for accessibility.
 */

interface SkeletonCardProps {
  rows?: number;
}

export function SkeletonCard({ rows = 2 }: SkeletonCardProps) {
  return (
    <div
      className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2"
      role="status"
      aria-label="Loading content"
      aria-busy="true"
    >
      {/* Title bar */}
      <div className="h-3 bg-slate-800 rounded skeleton-shimmer w-3/4" />
      {/* Subtitle */}
      <div className="h-2.5 bg-slate-800/70 rounded skeleton-shimmer w-1/2" />
      {/* Extra rows */}
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-2 bg-slate-800/50 rounded skeleton-shimmer"
          style={{ width: `${65 + i * 10}%`, animationDelay: `${i * 0.1}s` }}
        />
      ))}
    </div>
  );
}

export function SkeletonGrid() {
  return (
    <div
      className="grid grid-cols-3 gap-2"
      role="status"
      aria-label="Loading metrics"
      aria-busy="true"
    >
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="bg-slate-950 p-2 rounded-lg border border-slate-800 space-y-1.5"
        >
          <div className="h-2 bg-slate-800 rounded skeleton-shimmer w-2/3" style={{ animationDelay: `${i * 0.08}s` }} />
          <div className="h-3 bg-slate-800/70 rounded skeleton-shimmer w-1/2" style={{ animationDelay: `${i * 0.08 + 0.05}s` }} />
        </div>
      ))}
    </div>
  );
}

export function SkeletonList({ count = 3 }: { count?: number }) {
  return (
    <div
      className="space-y-2"
      role="status"
      aria-label="Loading investigation history"
      aria-busy="true"
    >
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2"
        >
          <div className="flex items-center justify-between">
            <div className="h-4 w-20 bg-slate-800 rounded skeleton-shimmer" style={{ animationDelay: `${i * 0.12}s` }} />
            <div className="h-3 w-12 bg-slate-800/60 rounded skeleton-shimmer" style={{ animationDelay: `${i * 0.12 + 0.06}s` }} />
          </div>
          <div className="h-3 bg-slate-800/80 rounded skeleton-shimmer w-5/6" style={{ animationDelay: `${i * 0.12 + 0.1}s` }} />
          <div className="h-2.5 bg-slate-800/50 rounded skeleton-shimmer w-2/3" style={{ animationDelay: `${i * 0.12 + 0.15}s` }} />
        </div>
      ))}
    </div>
  );
}

/** Inline single-line skeleton for small values */
export function SkeletonInline({ width = "w-20" }: { width?: string }) {
  return (
    <span
      className={`inline-block h-3 ${width} bg-slate-800 rounded skeleton-shimmer`}
      role="status"
      aria-label="Loading"
    />
  );
}

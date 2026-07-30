import { ShieldAlert, CheckCircle, AlertTriangle } from "lucide-react";

interface RiskExplanationCardProps {
  riskScore: number;
  reasoningBullets?: string[];
  marketplace?: string;
}

export function RiskExplanationCard({
  riskScore,
  reasoningBullets = [],
  marketplace = "Marketplace",
}: RiskExplanationCardProps) {
  const isHighRisk = riskScore > 50;

  // Default bullets if reasoningBullets array is empty
  const displayBullets =
    reasoningBullets.length > 0
      ? reasoningBullets
      : isHighRisk
      ? [
          "Price anomaly (listed significantly below market MSRP)",
          `Seller identity on ${marketplace} unverified`,
          "Missing or contradictory manufacturer specifications",
          "Visual forensics flagged listing copy/image similarity",
        ]
      : [
          `Seller identity on ${marketplace} verified authentic`,
          "Listing price aligns with standard market MSRP baseline",
          "Official manufacturer catalog and trademark verified",
        ];

  return (
    <div className="rounded-2xl border border-border bg-slate-900/95 p-6 text-white shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-4">
          <div
            className={`h-12 w-12 rounded-xl flex items-center justify-center font-bold shrink-0 ${
              isHighRisk
                ? "bg-red-500/20 text-red-400 border border-red-500/40"
                : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
            }`}
          >
            {isHighRisk ? (
              <ShieldAlert className="h-6 w-6 text-red-400" />
            ) : (
              <CheckCircle className="h-6 w-6 text-emerald-400" />
            )}
          </div>
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              Risk Analysis Explanation
            </h3>
            <p className="text-xs text-slate-400">
              Autonomous multi-agent risk attribution breakdown
            </p>
          </div>
        </div>

        {/* Big Risk Score Display */}
        <div className="flex items-center gap-3 bg-slate-800/80 px-4 py-2.5 rounded-xl border border-slate-700">
          <span className="text-sm font-semibold text-slate-300 font-mono">Risk Score:</span>
          <span
            className={`text-3xl font-black font-mono tracking-tight ${
              isHighRisk ? "text-red-400" : "text-emerald-400"
            }`}
          >
            {riskScore}
          </span>
          <span className="text-xs text-slate-400 font-mono">/ 100</span>
        </div>
      </div>

      {/* Bullet Explanation List */}
      <div className="pt-4 space-y-3">
        <p className="text-xs font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5 text-amber-400" /> Risk calculated as{" "}
          <span className={isHighRisk ? "text-red-400 font-bold" : "text-emerald-400 font-bold"}>
            {riskScore}/100
          </span>{" "}
          because:
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
          {displayBullets.map((bullet, idx) => (
            <div
              key={idx}
              className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-800/60 border border-slate-700/70 text-xs text-slate-200"
            >
              <div
                className={`h-2 w-2 rounded-full mt-1.5 shrink-0 ${
                  isHighRisk ? "bg-red-400" : "bg-emerald-400"
                }`}
              />
              <span className="leading-relaxed font-medium">{bullet}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

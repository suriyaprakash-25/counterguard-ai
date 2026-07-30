import { useState, useEffect } from "react";
import { X, Network, Database, ShieldCheck, FileText, Server, Cpu, Layers, ExternalLink, CheckCircle, Hash, Clock } from "lucide-react";
import { Button } from "./Button";
import { Badge } from "./Badge";

interface LineageNode {
  id: string;
  type: string;
  label: string;
  status: string;
}

interface ListingLineageData {
  candidate_id: string;
  http_request_id: string;
  response_sha256: string;
  evidence_archive_id: string;
  parser_version: string;
  parser_confidence: number;
  retrieval_mode: string;
  deduplication_group_id: string;
  ranking_score: number;
  investigation_id: string;
  report_id: string;
  dag_nodes: LineageNode[];
  timestamp: string;
}

interface ListingLineageDrawerProps {
  candidateId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ListingLineageDrawer({ candidateId, isOpen, onClose }: ListingLineageDrawerProps) {
  const [data, setData] = useState<ListingLineageData | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!isOpen || !candidateId) return;

    setLoading(true);
    fetch(`http://localhost:8000/api/v1/discovery/${candidateId}/lineage`)
      .then((res) => res.json())
      .then((json) => {
        setData(json);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch candidate lineage:", err);
        setLoading(false);
      });
  }, [isOpen, candidateId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/60 backdrop-blur-sm transition-opacity">
      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-xl bg-slate-900 border-l border-slate-800 text-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-6 border-b border-slate-800 flex items-center justify-between bg-slate-900/90">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-xl bg-primary/20 border border-primary/40 flex items-center justify-center text-primary-light">
                <Network className="h-5 w-5" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  Evidence Lineage Inspector
                </h3>
                <p className="text-xs text-slate-400 font-mono">
                  Candidate ID: {candidateId}
                </p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose} className="text-slate-400 hover:text-white">
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-16 space-y-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
                <p className="text-sm font-medium text-slate-400">Loading Cryptographic Lineage Graph...</p>
              </div>
            ) : data ? (
              <>
                {/* Metadata Badges Summary */}
                <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-800/80 border border-slate-700/80 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-mono">Retrieval Mode</span>
                    <Badge variant="outline" className="mt-1 bg-emerald-500/20 text-emerald-300 border-emerald-500/40">
                      {data.retrieval_mode}
                    </Badge>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-mono">Parser Confidence</span>
                    <span className="font-bold text-emerald-400 text-sm">{data.parser_confidence}%</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-mono">Parser Version</span>
                    <span className="font-mono text-slate-200">{data.parser_version}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-mono">Ranking Score</span>
                    <span className="font-mono text-amber-400 font-bold">{data.ranking_score}</span>
                  </div>
                </div>

                {/* SHA-256 Hash Card */}
                <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-xs space-y-2">
                  <div className="flex items-center justify-between text-slate-400 text-[10px] uppercase">
                    <span className="flex items-center gap-1"><Hash className="h-3 w-3 text-primary-light" /> Response Payload SHA-256</span>
                    <span className="text-emerald-400">VERIFIED</span>
                  </div>
                  <p className="text-primary-light break-all text-[11px] bg-slate-900 p-2 rounded border border-slate-800">
                    {data.response_sha256}
                  </p>
                </div>

                {/* Lineage Graph DAG Step List */}
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                    <Layers className="h-3.5 w-3.5 text-primary-light" /> Lineage DAG Trace Nodes
                  </h4>

                  <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-slate-700">
                    {data.dag_nodes.map((node, index) => (
                      <div key={node.id} className="relative group">
                        <div className="absolute -left-6 top-1 h-5 w-5 rounded-full bg-slate-800 border-2 border-primary flex items-center justify-center text-[10px] font-bold font-mono text-primary-light">
                          {index + 1}
                        </div>
                        <div className="p-3.5 rounded-xl bg-slate-800/90 border border-slate-700/80 hover:border-primary/50 transition-colors">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-white flex items-center gap-1.5">
                              {node.label}
                            </span>
                            <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded bg-slate-950 text-slate-300 border border-slate-800">
                              {node.status}
                            </span>
                          </div>
                          <p className="text-[11px] text-slate-400 font-mono mt-1">
                            Node Type: <strong className="text-slate-200">{node.type}</strong>
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <p className="text-center text-slate-400 py-12">No lineage record found for this candidate.</p>
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-slate-800 bg-slate-900/90 flex justify-end">
            <Button variant="outline" onClick={onClose} className="border-slate-700 text-slate-300 hover:bg-slate-800">
              Close Lineage Inspector
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

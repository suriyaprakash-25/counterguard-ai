import { Card, CardHeader, CardTitle, CardContent } from "../common/Card";
import { Badge } from "../common/Badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../common/Table";
import {
  Bot, Clock, AlertCircle, FileText, Image as ImageIcon, Link2, Server, Search, CheckCircle2, XCircle
} from "lucide-react";
import type {
  InvestigationWorkspaceDetails, TimelineEvent, EvidenceItem,
  GraphNodePreview, MemoryContext, ConsensusDetails, AgentActivity
} from "../../types/investigations";

// --- 2. Summary Card ---
export function SummaryCard({ data }: { data: InvestigationWorkspaceDetails }) {
  return (
    <Card className="border-l-4 border-l-primary">
      <CardContent className="p-6">
        <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
          <div className="space-y-1 min-w-[200px]">
            <p className="text-sm font-medium text-muted">Final Verdict</p>
            <div className="flex items-center gap-2">
              <span className={`text-2xl font-bold ${
                data.finalVerdict === 'fraud' ? 'text-danger' :
                data.finalVerdict === 'authentic' ? 'text-success' : 'text-warning'
              }`}>
                {data.finalVerdict.toUpperCase()}
              </span>
              <Badge variant="outline">{data.verdictConfidence}% Confidence</Badge>
            </div>
          </div>
          <div className="flex-1 space-y-2 border-l border-border pl-6">
            <h4 className="text-sm font-semibold text-slate-900">AI Summary</h4>
            <p className="text-sm text-slate-700 leading-relaxed">{data.aiSummary}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// --- 3. Timeline ---
export function Timeline({ events }: { events: TimelineEvent[] }) {
  const getIcon = (type: string) => {
    switch(type) {
      case 'agent': return <Bot className="h-4 w-4 text-primary" />;
      case 'alert': return <AlertCircle className="h-4 w-4 text-danger" />;
      case 'memory': return <Server className="h-4 w-4 text-warning" />;
      default: return <Clock className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Investigation Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
          {events.map((event) => (
            <div key={event.id} className={`relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active`}>
              <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-100 text-slate-500 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2">
                {getIcon(event.iconType)}
              </div>
              <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-border bg-surface shadow-sm">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="font-semibold text-sm text-slate-900">{event.title}</h4>
                  <span className="text-xs text-muted">{new Date(event.timestamp).toLocaleTimeString()}</span>
                </div>
                <p className="text-sm text-slate-600">{event.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// --- 4. Evidence ---
export function EvidenceSection({ evidence }: { evidence: EvidenceItem[] }) {
  const getIcon = (type: string) => {
    switch(type) {
      case 'image': return <ImageIcon className="h-5 w-5 text-primary" />;
      case 'metadata': return <Server className="h-5 w-5 text-warning" />;
      case 'link': return <Link2 className="h-5 w-5 text-success" />;
      default: return <FileText className="h-5 w-5 text-slate-500" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Collected Evidence</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {evidence.map(item => (
          <div key={item.id} className="p-4 rounded-lg border border-border bg-slate-50">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                {getIcon(item.type)}
                <span className="text-sm font-semibold capitalize">{item.type}</span>
              </div>
              <Badge variant="outline">{item.confidence}% Conf</Badge>
            </div>
            <p className="text-sm text-slate-700 mb-3">{item.description}</p>
            <p className="text-xs text-muted font-mono bg-white px-2 py-1 rounded inline-block border border-slate-200">
              Source: {item.source}
            </p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

// --- 5. Graph Intelligence ---
export function GraphIntelligencePreview({ nodes }: { nodes: GraphNodePreview[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Graph Intelligence</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="bg-slate-50 rounded-lg border border-border border-dashed p-8 text-center flex flex-col items-center">
          <div className="flex flex-wrap justify-center gap-3 mb-4">
            {nodes.map(node => (
              <Badge key={node.id} variant="default" className="px-3 py-1">
                {node.label} ({node.type})
              </Badge>
            ))}
          </div>
          <p className="text-sm text-muted">Placeholder for interactive Cytoscape GraphRAG visualization.</p>
        </div>
      </CardContent>
    </Card>
  );
}

// --- 6. Memory Context ---
export function MemoryContextCard({ memory }: { memory: MemoryContext }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Memory Context</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-6 md:grid-cols-2">
        <div className="space-y-4">
          <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-border">
            <span className="text-sm text-slate-600">Previous Investigations</span>
            <span className="font-bold text-slate-900">{memory.previousInvestigations}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-border">
            <span className="text-sm text-slate-600">Semantic Matches</span>
            <span className="font-bold text-slate-900">{memory.semanticMatches}</span>
          </div>
          <div className="flex justify-between items-center p-3 bg-slate-50 rounded-lg border border-border">
            <span className="text-sm text-slate-600">Historical Risk Score</span>
            <span className="font-bold text-danger">{memory.historicalRisk}</span>
          </div>
        </div>
        <div>
          <h4 className="text-sm font-semibold mb-3">Known Patterns</h4>
          <ul className="space-y-2">
            {memory.knownPatterns.map((pattern, idx) => (
              <li key={idx} className="flex items-center gap-2 text-sm text-slate-700">
                <Search className="h-4 w-4 text-muted" /> {pattern}
              </li>
            ))}
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}

// --- 7. Consensus ---
export function ConsensusCard({ consensus }: { consensus: ConsensusDetails }) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Multi-Agent Consensus</CardTitle>
          <Badge variant="success">Agreement Score: {consensus.agreementScore}%</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <p className="text-sm text-slate-700">{consensus.explanation}</p>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          {consensus.agentVotes.map((vote, idx) => (
            <div key={idx} className="p-3 rounded-lg border border-border bg-surface text-center">
              <p className="text-xs font-semibold text-slate-900 mb-1">{vote.agent}</p>
              <Badge variant={vote.vote === 'fraud' ? 'danger' : 'success'} className="mb-2 uppercase">
                {vote.vote}
              </Badge>
              <p className="text-xs text-muted">{vote.confidence}% Conf</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// --- 8. Explainability & 9. Recommendations ---
export function ExplainabilityAndRecs({ data }: { data: InvestigationWorkspaceDetails }) {
  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Explainability</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-700 leading-relaxed">
            {data.explainability.reasoning}
          </p>
          <div className="mt-4 pt-4 border-t border-border">
            <span className="text-xs font-semibold text-muted uppercase">Supporting Evidence IDs</span>
            <div className="flex flex-wrap gap-2 mt-2">
              {data.explainability.supportingEvidenceIds.map(id => (
                <Badge key={id} variant="outline" className="font-mono">{id}</Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Recommended Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3">
            {data.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg border border-border">
                <CheckCircle2 className="h-5 w-5 text-primary shrink-0 mt-0.5" />
                <span className="text-sm text-slate-800">{rec}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

// --- 10. Agent Activity ---
export function AgentActivityTable({ activities }: { activities: AgentActivity[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Agent Execution Log</CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Agent</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Runtime (ms)</TableHead>
              <TableHead>Confidence</TableHead>
              <TableHead className="text-right">Timestamp</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {activities.map(activity => (
              <TableRow key={activity.id}>
                <TableCell className="font-medium flex items-center gap-2">
                  <Bot className="h-4 w-4 text-slate-400" />
                  {activity.agent}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1.5">
                    {activity.status === 'success' ? <CheckCircle2 className="h-4 w-4 text-success" /> :
                     activity.status === 'failed' ? <XCircle className="h-4 w-4 text-danger" /> :
                     <Clock className="h-4 w-4 text-warning" />}
                    <span className="text-sm capitalize">{activity.status}</span>
                  </div>
                </TableCell>
                <TableCell className="font-mono text-sm">{activity.runtimeMs}ms</TableCell>
                <TableCell>
                  {activity.confidence !== null ? `${activity.confidence}%` : '-'}
                </TableCell>
                <TableCell className="text-right text-muted text-sm">
                  {new Date(activity.timestamp).toLocaleTimeString()}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}

import { SectionCard } from "../../../components/common/SectionCard";
import { Badge } from "../../../components/common/Badge";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "../../../components/common/Table";
import { LoadingSkeleton } from "../../../components/common/LoadingSkeleton";
import { ErrorState } from "../../../components/common/ErrorState";
import {
  useIntelligenceSummary, useKnownSellers, useFraudRings, useKnownPatterns,
  useRepeatedImages, useRepeatedPhones, useRepeatedInvoices,
  useMemoryInsights, useKnowledgeGraphStats
} from "../hooks/useIntelligence";
import {
  Users, Network, Image as ImageIcon, FileText, Brain, Database, ShieldAlert, Link2
} from "lucide-react";

// --- SECTION 2: Global Summary ---
export function GlobalSummaryWidget() {
  const { data, isLoading, isError, refetch } = useIntelligenceSummary();
  if (isLoading) return <LoadingSkeleton className="h-32 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load summary" onRetry={() => refetch()} />;

  const metrics = [
    { label: "Known Sellers", value: data.knownSellers, icon: Users },
    { label: "Fraud Rings", value: data.knownFraudRings, icon: Network },
    { label: "Counterfeit Listings", value: data.knownCounterfeitListings, icon: ShieldAlert },
    { label: "Repeated Assets", value: data.repeatedAssets, icon: ImageIcon },
    { label: "Past Investigations", value: data.historicalInvestigations, icon: FileText },
    { label: "Memory Episodes", value: data.memoryEpisodes, icon: Brain },
    { label: "Graph Nodes", value: data.graphNodes, icon: Database },
    { label: "Graph Edges", value: data.graphRelationships, icon: Link2 },
  ];

  return (
    <SectionCard title="Global Intelligence Summary">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div key={idx} className="p-4 rounded-lg border border-border bg-slate-50 flex items-center justify-between">
              <div>
                <p className="text-xs font-medium text-muted mb-1">{m.label}</p>
                <p className="text-xl font-bold text-slate-900">{m.value.toLocaleString()}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-slate-200 flex items-center justify-center">
                <Icon className="h-4 w-4 text-slate-600" />
              </div>
            </div>
          );
        })}
      </div>
    </SectionCard>
  );
}

// --- SECTION 3: Known Sellers ---
export function KnownSellersWidget() {
  const { data, isLoading, isError, refetch } = useKnownSellers();
  if (isLoading) return <LoadingSkeleton className="h-64 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load sellers" onRetry={() => refetch()} />;

  return (
    <SectionCard title="Known Sellers" description="Entities tracked across multiple marketplaces.">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Seller Name</TableHead>
            <TableHead>Marketplace</TableHead>
            <TableHead>Risk</TableHead>
            <TableHead>Investigations</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map(seller => (
            <TableRow key={seller.id}>
              <TableCell className="font-medium">{seller.name}</TableCell>
              <TableCell>{seller.marketplace}</TableCell>
              <TableCell>
                <Badge variant={seller.riskScore > 80 ? "danger" : seller.riskScore > 50 ? "warning" : "success"}>
                  {seller.riskScore}
                </Badge>
              </TableCell>
              <TableCell>{seller.historicalInvestigations}</TableCell>
              <TableCell>
                <Badge variant={seller.status === 'banned' ? "danger" : seller.status === 'monitoring' ? "warning" : "success"} className="uppercase">
                  {seller.status}
                </Badge>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </SectionCard>
  );
}

// --- SECTION 4: Fraud Rings ---
export function FraudRingsWidget() {
  const { data, isLoading, isError, refetch } = useFraudRings();
  if (isLoading) return <LoadingSkeleton className="h-64 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load rings" onRetry={() => refetch()} />;

  return (
    <SectionCard title="Fraud Rings" description="Coordinated malicious entity networks.">
      <div className="grid gap-4 md:grid-cols-2">
        {data.map(ring => (
          <div key={ring.id} className="p-4 rounded-lg border border-border bg-surface">
            <div className="flex justify-between items-start mb-2">
              <h4 className="font-semibold text-slate-900">{ring.name}</h4>
              <Badge variant="danger">Avg Risk: {ring.averageRisk}</Badge>
            </div>
            <div className="flex gap-4 text-sm text-slate-600">
              <span>{ring.members} Members</span>
              <span>{ring.connectedSellers} Sellers</span>
              <span>{ring.connectedListings} Listings</span>
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

// --- SECTION 5: Known Patterns ---
export function KnownPatternsWidget() {
  const { data, isLoading, isError, refetch } = useKnownPatterns();
  if (isLoading) return <LoadingSkeleton className="h-48 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load patterns" onRetry={() => refetch()} />;

  return (
    <SectionCard title="Known Patterns" description="Recurring behavioral indicators of fraud.">
      <div className="grid gap-4 md:grid-cols-3">
        {data.map(pattern => (
          <div key={pattern.id} className="p-4 rounded-lg border border-border bg-slate-50 border-l-4 border-l-warning">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-semibold uppercase text-muted">{pattern.type.replace('_', ' ')}</span>
              <Badge variant="outline">{pattern.occurrences} Occurrences</Badge>
            </div>
            <h4 className="font-semibold text-sm text-slate-900 mb-1">{pattern.title}</h4>
            <p className="text-xs text-slate-600">{pattern.description}</p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

// --- SECTION 6: Repeated Images ---
export function RepeatedImagesWidget() {
  const { data, isLoading, isError, refetch } = useRepeatedImages();
  if (isLoading) return <LoadingSkeleton className="h-64 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load images" onRetry={() => refetch()} />;

  return (
    <SectionCard title="Repeated Images" description="Media assets reused across multiple suspicious listings.">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {data.map(img => (
          <div key={img.id} className="rounded-lg border border-border bg-surface overflow-hidden">
            <div className="h-32 bg-slate-200 flex items-center justify-center border-b border-border">
              <ImageIcon className="h-8 w-8 text-slate-400" />
            </div>
            <div className="p-3">
              <Badge variant="default" className="mb-2">{img.occurrences} Occurrences</Badge>
              <div className="text-xs text-muted space-y-1">
                <p>Sellers: {img.connectedSellers}</p>
                <p>Listings: {img.connectedListings}</p>
                <p>Similarity: {(img.similarityScore * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

// --- SECTION 7 & 8: Repeated Phones & Invoices ---
export function RepeatedPhonesInvoicesWidget() {
  const phones = useRepeatedPhones();
  const invoices = useRepeatedInvoices();

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <SectionCard title="Repeated Phones">
        {phones.isLoading ? <LoadingSkeleton className="h-32 w-full" /> :
         phones.isError || !phones.data ? <ErrorState message="Failed" onRetry={() => phones.refetch()} /> : (
           <Table>
             <TableHeader><TableRow><TableHead>Phone</TableHead><TableHead>Occurrences</TableHead><TableHead>Risk</TableHead></TableRow></TableHeader>
             <TableBody>
               {phones.data.map(phone => (
                 <TableRow key={phone.id}>
                   <TableCell className="font-mono">{phone.phoneNumber}</TableCell>
                   <TableCell>{phone.occurrences}</TableCell>
                   <TableCell><Badge variant="danger">{phone.riskScore}</Badge></TableCell>
                 </TableRow>
               ))}
             </TableBody>
           </Table>
         )}
      </SectionCard>
      <SectionCard title="Repeated Invoices">
        {invoices.isLoading ? <LoadingSkeleton className="h-32 w-full" /> :
         invoices.isError || !invoices.data ? <ErrorState message="Failed" onRetry={() => invoices.refetch()} /> : (
           <Table>
             <TableHeader><TableRow><TableHead>Invoice ID</TableHead><TableHead>Occurrences</TableHead><TableHead>Sellers</TableHead></TableRow></TableHeader>
             <TableBody>
               {invoices.data.map(inv => (
                 <TableRow key={inv.id}>
                   <TableCell className="font-mono">{inv.invoiceId}</TableCell>
                   <TableCell>{inv.occurrences}</TableCell>
                   <TableCell>{inv.associatedSellers}</TableCell>
                 </TableRow>
               ))}
             </TableBody>
           </Table>
         )}
      </SectionCard>
    </div>
  );
}

// --- SECTION 9: Semantic Memory Insights ---
export function SemanticMemoryWidget() {
  const { data, isLoading, isError, refetch } = useMemoryInsights();
  if (isLoading) return <LoadingSkeleton className="h-48 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load memory insights" onRetry={() => refetch()} />;

  return (
    <SectionCard title="Semantic Memory Insights" description="AI-generated observations across historical data.">
      <div className="grid gap-4 md:grid-cols-2">
        {data.map(insight => (
          <div key={insight.id} className="p-4 rounded-lg border border-border bg-slate-50">
            <div className="flex justify-between items-center mb-2">
              <h4 className="font-semibold text-sm text-slate-900">{insight.title}</h4>
              <Badge variant="outline">{insight.confidence}% Conf</Badge>
            </div>
            <p className="text-sm text-slate-600 mb-2">{insight.description}</p>
            <p className="text-xs text-muted italic">Context: {insight.context}</p>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}

// --- SECTION 10: Graph Stats ---
export function GraphStatsWidget() {
  const { data, isLoading, isError, refetch } = useKnowledgeGraphStats();
  if (isLoading) return <LoadingSkeleton className="h-32 w-full" />;
  if (isError || !data) return <ErrorState message="Failed to load graph stats" onRetry={() => refetch()} />;

  return (
    <SectionCard title="Knowledge Graph Statistics" description="Topological intelligence metrics from Neo4j.">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: "Nodes", value: data.nodeCount.toLocaleString() },
          { label: "Relationships", value: data.relationshipCount.toLocaleString() },
          { label: "Communities", value: data.communities.toLocaleString() },
          { label: "Max Ring Size", value: data.largestFraudRingSize.toLocaleString() },
          { label: "Avg Connectivity", value: data.averageConnectivity },
          { label: "Graph Density", value: data.graphDensity }
        ].map((stat, idx) => (
           <div key={idx} className="text-center p-3 rounded bg-slate-50 border border-border">
             <p className="text-xs text-muted mb-1">{stat.label}</p>
             <p className="font-semibold text-slate-900">{stat.value}</p>
           </div>
        ))}
      </div>
    </SectionCard>
  );
}

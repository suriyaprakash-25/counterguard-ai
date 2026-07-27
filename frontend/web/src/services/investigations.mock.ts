import type { InvestigationSummary, InvestigationWorkspaceDetails } from "../types/investigations";

export const MOCK_INVESTIGATIONS: InvestigationSummary[] = [
  {
    id: "INV-9001",
    name: "Suspicious iPhone 15 Pro Batch",
    marketplace: "Amazon",
    status: "completed",
    riskScore: 92,
    investigationType: "Product Authenticity",
    plannerPriority: "critical",
    agentCount: 5,
    createdAt: "2026-07-27T08:15:00Z",
    lastUpdated: "2026-07-27T08:45:00Z",
  },
  {
    id: "INV-9002",
    name: "Grey Market Sony Headphones",
    marketplace: "Flipkart",
    status: "in_progress",
    riskScore: 68,
    investigationType: "Parallel Import",
    plannerPriority: "high",
    agentCount: 3,
    createdAt: "2026-07-27T07:30:00Z",
    lastUpdated: "2026-07-27T08:20:00Z",
  },
  {
    id: "INV-9003",
    name: "Rolex Daytona Replicas",
    marketplace: "eBay",
    status: "completed",
    riskScore: 99,
    investigationType: "Counterfeit",
    plannerPriority: "critical",
    agentCount: 6,
    createdAt: "2026-07-26T18:20:00Z",
    lastUpdated: "2026-07-26T19:10:00Z",
  },
  {
    id: "INV-9004",
    name: "Unauthorized Samsung Chargers",
    marketplace: "Temu",
    status: "pending",
    riskScore: 45,
    investigationType: "IP Violation",
    plannerPriority: "medium",
    agentCount: 2,
    createdAt: "2026-07-26T14:10:00Z",
    lastUpdated: "2026-07-26T14:10:00Z",
  },
  {
    id: "INV-9005",
    name: "Fake Nike Air Max",
    marketplace: "Alibaba",
    status: "completed",
    riskScore: 88,
    investigationType: "Counterfeit",
    plannerPriority: "high",
    agentCount: 4,
    createdAt: "2026-07-25T11:00:00Z",
    lastUpdated: "2026-07-25T12:30:00Z",
  }
];

export const MOCK_WORKSPACE_DETAILS: InvestigationWorkspaceDetails = {
  ...MOCK_INVESTIGATIONS[0],
  finalVerdict: "fraud",
  verdictConfidence: 94,
  aiSummary: "The seller 'GlobalTech Store' is operating a highly sophisticated counterfeit operation. They are using stolen product imagery, matching a known fraud network's phone number, and listing products significantly below wholesale cost. The OCR Agent confirmed fake serial numbers on packaging.",
  timeline: [
    { id: "t1", timestamp: "2026-07-27T08:15:00Z", title: "Marketplace Anomaly Detected", description: "Listing found 45% below market average.", iconType: "system" },
    { id: "t2", timestamp: "2026-07-27T08:16:00Z", title: "Planner Generated Investigation", description: "Dispatched 5 agents to collect evidence.", iconType: "agent" },
    { id: "t3", timestamp: "2026-07-27T08:20:00Z", title: "Vision Agent Completed", description: "Found mismatch in packaging font weights.", iconType: "agent" },
    { id: "t4", timestamp: "2026-07-27T08:25:00Z", title: "OCR Agent Completed", description: "Extracted serial number 'A1B2C3D4' which matches known counterfeit list.", iconType: "agent" },
    { id: "t5", timestamp: "2026-07-27T08:35:00Z", title: "Graph Intelligence Updated", description: "Linked seller phone number to 3 previously banned accounts.", iconType: "system" },
    { id: "t6", timestamp: "2026-07-27T08:40:00Z", title: "Consensus Reached", description: "Agents voted 4-0 for 'Fraud'.", iconType: "system" },
    { id: "t7", timestamp: "2026-07-27T08:45:00Z", title: "Alert Dispatched", description: "Critical alert sent to marketplace enforcement team.", iconType: "alert" }
  ],
  evidence: [
    { id: "e1", type: "image", confidence: 98, description: "Packaging font weight is bolder than authentic Apple packaging.", source: "Vision Agent" },
    { id: "e2", type: "text", confidence: 100, description: "Serial number extracted from user reviews matches known counterfeit batch.", source: "OCR Agent" },
    { id: "e3", type: "metadata", confidence: 85, description: "Seller IP address routes through a known VPN endpoint frequently used by banned sellers.", source: "Network Agent" },
  ],
  graphPreview: [
    { id: "n1", type: "seller", label: "GlobalTech Store", relationship: "Target Entity" },
    { id: "n2", type: "phone", label: "+1 555-0198", relationship: "Shared Contact" },
    { id: "n3", type: "seller", label: "BestDeals LLC", relationship: "Banned Seller" },
    { id: "n4", type: "listing", label: "iPhone 15 Pro", relationship: "Current Listing" }
  ],
  memoryContext: {
    previousInvestigations: 3,
    semanticMatches: 12,
    historicalRisk: 88,
    knownPatterns: ["Bait and switch shipping", "Recycled serial numbers", "Burner VOIP numbers"]
  },
  consensus: {
    agreementScore: 100,
    explanation: "All specialized agents strongly agree on a fraudulent verdict based on converging evidence from visual, text, and network vectors.",
    agentVotes: [
      { agent: "Vision Agent", vote: "fraud", confidence: 95 },
      { agent: "OCR Agent", vote: "fraud", confidence: 99 },
      { agent: "Network Agent", vote: "fraud", confidence: 85 },
      { agent: "Seller Intel Agent", vote: "fraud", confidence: 92 }
    ]
  },
  explainability: {
    reasoning: "The system reached a 'Fraud' verdict primarily because the OCR Agent identified a recycled serial number (A1B2C3D4) that has been flagged in 12 previous investigations (Semantic Memory). This finding was corroborated by the Vision Agent, which detected non-standard packaging typography. Furthermore, the Knowledge Graph (Neo4j) linked the seller's registration phone number to a previously banned entity ('BestDeals LLC'), establishing a clear pattern of evasion.",
    supportingEvidenceIds: ["e1", "e2", "e3"]
  },
  recommendations: [
    "Issue immediate takedown request to Amazon Trust & Safety.",
    "Add phone number '+1 555-0198' to global blocklist.",
    "Schedule recurring scan for 'GlobalTech Store' director name.",
    "Extract all associated ASINs for bulk analysis."
  ],
  agentActivity: [
    { id: "a1", agent: "Coordinator Agent", status: "success", runtimeMs: 120, confidence: null, timestamp: "2026-07-27T08:15:00Z" },
    { id: "a2", agent: "Planner Agent", status: "success", runtimeMs: 850, confidence: null, timestamp: "2026-07-27T08:16:00Z" },
    { id: "a3", agent: "Vision Agent", status: "success", runtimeMs: 3400, confidence: 95, timestamp: "2026-07-27T08:20:00Z" },
    { id: "a4", agent: "OCR Agent", status: "success", runtimeMs: 2100, confidence: 99, timestamp: "2026-07-27T08:25:00Z" },
    { id: "a5", agent: "Network Agent", status: "success", runtimeMs: 1500, confidence: 85, timestamp: "2026-07-27T08:30:00Z" },
    { id: "a6", agent: "Seller Intel Agent", status: "success", runtimeMs: 4200, confidence: 92, timestamp: "2026-07-27T08:33:00Z" },
    { id: "a7", agent: "Consensus Engine", status: "success", runtimeMs: 500, confidence: 100, timestamp: "2026-07-27T08:40:00Z" },
  ]
};

export const MOCK_GRAPH_DTO = {
  elements: {
    nodes: [
      { data: { id: "N1", label: "GlobalTech Store", type: "seller", risk: 92, props: { registered: "2023", country: "CN" } } },
      { data: { id: "N2", label: "iPhone 15 Pro Max", type: "product", risk: 85, props: { brand: "Apple", price: "$499" } } },
      { data: { id: "N3", label: "+1 555-0198", type: "phone", risk: 99, props: { provider: "Twilio", type: "VOIP" } } },
      { data: { id: "N4", label: "Amazon", type: "marketplace", risk: 0, props: { region: "US" } } },
      { data: { id: "N5", label: "BestDeals LLC", type: "seller", risk: 88, props: { status: "banned" } } },
      { data: { id: "N6", label: "INV-9001", type: "investigation", risk: 100, props: { status: "fraud" } } },
      { data: { id: "N7", label: "Fake AirPods", type: "product", risk: 95, props: { brand: "Apple" } } },
      { data: { id: "N8", label: "Recycled Packaging", type: "pattern", risk: 80, props: { confidence: 0.92 } } },
    ],
    edges: [
      { data: { id: "E1", source: "N1", target: "N2", label: "LISTED" } },
      { data: { id: "E2", source: "N1", target: "N3", label: "USES_PHONE" } },
      { data: { id: "E3", source: "N5", target: "N3", label: "USES_PHONE" } },
      { data: { id: "E4", source: "N2", target: "N4", label: "ON_MARKETPLACE" } },
      { data: { id: "E5", source: "N6", target: "N1", label: "INVESTIGATED" } },
      { data: { id: "E6", source: "N1", target: "N7", label: "LISTED" } },
      { data: { id: "E7", source: "N7", target: "N8", label: "MATCHES_PATTERN" } },
    ]
  }
};

export const MOCK_GRAPH_STATS_DTO = {
  n_count: 12500,
  r_count: 34200,
  comm_count: 320,
  largest_comp: 840,
  avg_deg: 2.7,
  top_seller: "GlobalTech Store"
};

export const MOCK_ALERTS_DTO = [
  {
    _id: "ALT-001",
    level: "critical",
    headline: "Massive Fraud Ring Expansion Detected",
    platform: "Global",
    time: "2026-07-27T08:45:00Z",
    case_id: "INV-9001",
    state: "new",
    risk: 98,
    category: "Fraud Ring Expansion",
    desc: "The Shenzhen Electronics Ring has expanded by 12 new seller accounts in the last hour across Amazon and eBay.",
    entities: [
      { e_id: "R-12", e_type: "ring", e_name: "Shenzhen Electronics Ring" },
      { e_id: "S-88", e_type: "seller", e_name: "TechBros Direct" }
    ],
    actions: ["Isolate new seller nodes", "Issue marketplace takedown API call"]
  },
  {
    _id: "ALT-002",
    level: "high",
    headline: "High Confidence Counterfeit AirPods",
    platform: "Temu",
    time: "2026-07-27T07:30:00Z",
    case_id: "INV-9004",
    state: "new",
    risk: 85,
    category: "Counterfeit Detection",
    desc: "Consensus engine reached 100% agreement on counterfeit status based on Vision and OCR agent findings.",
    entities: [
      { e_id: "P-44", e_type: "product", e_name: "AirPods Pro Max" },
      { e_id: "IMG-02", e_type: "image", e_name: "Recycled Packaging Image" }
    ],
    actions: ["Export evidence report", "Ban seller account locally"]
  },
  {
    _id: "ALT-003",
    level: "medium",
    headline: "Grey Market Sony Headphones Surge",
    platform: "Flipkart",
    time: "2026-07-26T18:20:00Z",
    case_id: "INV-9002",
    state: "acknowledged",
    risk: 68,
    category: "Grey Market",
    desc: "Significant volume increase in unauthorized Sony headphone sales detected.",
    entities: [
      { e_id: "B-Sony", e_type: "brand", e_name: "Sony" }
    ],
    actions: ["Monitor volume for 24h", "Cross-reference with authorized distributor list"]
  }
];

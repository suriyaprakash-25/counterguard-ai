import { describe, it, expect } from "vitest";
import { IntelligenceMapper } from "../services/intelligence.mapper";
import { MOCK_SUMMARY_DTO } from "../services/intelligence.mock";

describe("Intelligence Mapper", () => {
  it("maps summary DTO to frontend model", () => {
    const result = IntelligenceMapper.toSummary(MOCK_SUMMARY_DTO);
    expect(result.knownSellers).toBe(12450);
    expect(result.graphNodes).toBe(125000);
    expect(result.knownCounterfeitListings).toBe(45210);
  });
});

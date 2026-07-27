import { describe, it, expect } from "vitest";
import { AlertsMapper } from "../services/alerts.mapper";
import { MOCK_ALERTS_DTO } from "../services/alerts.mock";

describe("Alerts Mapper", () => {
  it("maps alerts DTO to summary", () => {
    const result = AlertsMapper.toSummary(MOCK_ALERTS_DTO[0]);
    expect(result.id).toBe("ALT-001");
    expect(result.severity).toBe("critical");
    expect(result.status).toBe("new");
  });

  it("maps alerts DTO to details", () => {
    const result = AlertsMapper.toDetails(MOCK_ALERTS_DTO[0]);
    expect(result.id).toBe("ALT-001");
    expect(result.type).toBe("Fraud Ring Expansion");
    expect(result.relatedEntities).toHaveLength(2);
    expect(result.recommendedActions).toHaveLength(2);
  });
});

import { describe, it, expect } from "vitest";
import { SettingsMapper } from "../services/settings.mapper";
import { MOCK_SETTINGS_DTO } from "../services/settings.mock";

describe("Settings Mapper", () => {
  it("maps settings DTO correctly", () => {
    const result = SettingsMapper.toSettingsData(MOCK_SETTINGS_DTO);
    expect(result.version).toBe("1.5.0-sprint15");
    expect(result.systemStatus).toHaveLength(5);
    expect(result.systemStatus[0].service).toBe("FastAPI Core");
    expect(result.systemStatus[0].status).toBe("operational");
  });
});

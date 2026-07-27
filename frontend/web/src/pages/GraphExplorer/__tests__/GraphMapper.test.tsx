import { describe, it, expect } from "vitest";
import { GraphMapper } from "../services/graph.mapper";
import { MOCK_GRAPH_DTO, MOCK_GRAPH_STATS_DTO } from "../services/graph.mock";

describe("Graph Mapper", () => {
  it("maps graph DTO nodes and edges", () => {
    const result = GraphMapper.toGraphData(MOCK_GRAPH_DTO);
    expect(result.nodes).toHaveLength(8);
    expect(result.edges).toHaveLength(7);
    expect(result.nodes[0].label).toBe("GlobalTech Store");
    expect(result.nodes[0].properties?.registered).toBe("2023");
  });

  it("maps graph stats DTO", () => {
    const result = GraphMapper.toStatistics(MOCK_GRAPH_STATS_DTO);
    expect(result.totalNodes).toBe(12500);
    expect(result.averageDegree).toBe(2.7);
  });
});

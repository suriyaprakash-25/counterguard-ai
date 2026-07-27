import { useQuery } from "@tanstack/react-query";
import { GraphRepository } from "../services/graph.repository";

export const useGraph = () => {
  return useQuery({
    queryKey: ["graph", "data"],
    queryFn: GraphRepository.getGraphData,
    staleTime: 5 * 60 * 1000,
  });
};

export const useGraphStats = () => {
  return useQuery({
    queryKey: ["graph", "stats"],
    queryFn: GraphRepository.getGraphStats
  });
};

export const useNodeDetails = (nodeId: string | null) => {
  return useQuery({
    queryKey: ["graph", "node", nodeId],
    queryFn: () => GraphRepository.getNodeDetails(nodeId!),
    enabled: !!nodeId
  });
};

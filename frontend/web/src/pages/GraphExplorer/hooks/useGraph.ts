import { useQuery } from "@tanstack/react-query";
import { graphService } from "../services/graph.service";

export const useGraphData = () => {
  return useQuery({
    queryKey: ["graph", "data"],
    queryFn: graphService.getGraphData
  });
};

export const useGraphStats = () => {
  return useQuery({
    queryKey: ["graph", "stats"],
    queryFn: graphService.getGraphStats
  });
};

export const useNodeDetails = (nodeId: string | null) => {
  return useQuery({
    queryKey: ["graph", "node", nodeId],
    queryFn: () => graphService.getNodeDetails(nodeId!),
    enabled: !!nodeId
  });
};

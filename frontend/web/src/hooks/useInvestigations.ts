import { useQuery } from "@tanstack/react-query";
import { investigationService } from "../services/investigations.service";

export const useInvestigations = () => {
  return useQuery({
    queryKey: ["investigations"],
    queryFn: investigationService.getInvestigations,
  });
};

export const useInvestigation = (id: string) => {
  return useQuery({
    queryKey: ["investigation", id],
    queryFn: () => investigationService.getInvestigationDetails(id),
    enabled: !!id,
  });
};

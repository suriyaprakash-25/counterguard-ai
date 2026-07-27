import { useQuery } from "@tanstack/react-query";
import { settingsService } from "../services/settings.service";

export const useSettings = () => {
  return useQuery({
    queryKey: ["settings", "config"],
    queryFn: settingsService.getSettings
  });
};

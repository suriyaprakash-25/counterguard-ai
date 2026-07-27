import { useQuery } from "@tanstack/react-query";
import { SettingsRepository } from "../services/settings.repository";

export const useSettings = () => {
  return useQuery({
    queryKey: ["settings", "config"],
    queryFn: SettingsRepository.getSettings
  });
};

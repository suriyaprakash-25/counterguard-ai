import { createContext, useState, type ReactNode } from 'react';
import { DEFAULT_FEATURE_FLAGS, type FeatureFlagsConfig } from '../config/featureFlags';

interface AppContextState {
  currentUser: { name: string; role: string; id: string } | null;
  currentOrganization: { name: string; id: string } | null;
  theme: 'light' | 'dark';
  featureFlags: FeatureFlagsConfig;
  unreadNotifications: number;
}

interface AppContextValue extends AppContextState {
  setTheme: (theme: 'light' | 'dark') => void;
  setUnreadNotifications: (count: number) => void;
}

const defaultState: AppContextState = {
  currentUser: { name: "Agent Supervisor", role: "admin", id: "U-01" },
  currentOrganization: { name: "CounterGuard Inc", id: "ORG-01" },
  theme: 'light',
  featureFlags: DEFAULT_FEATURE_FLAGS,
  unreadNotifications: 0
};

export const AppContext = createContext<AppContextValue>({
  ...defaultState,
  setTheme: () => {},
  setUnreadNotifications: () => {}
});

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppContextState>(defaultState);

  const setTheme = (theme: 'light' | 'dark') => setState(prev => ({ ...prev, theme }));
  const setUnreadNotifications = (unreadNotifications: number) => setState(prev => ({ ...prev, unreadNotifications }));

  return (
    <AppContext.Provider value={{ ...state, setTheme, setUnreadNotifications }}>
      {children}
    </AppContext.Provider>
  );
}

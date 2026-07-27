import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, LoginCredentials } from './models';
import { AuthRepository } from './repository';
import { getAuthToken, setAuthToken, removeAuthToken } from '../../shared/api/auth';
import { useQueryClient } from '@tanstack/react-query';
import { eventBus } from '../../events/eventBus';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  useEffect(() => {
    const initAuth = async () => {
      const token = getAuthToken();
      if (token) {
        try {
          const userData = await AuthRepository.getMe();
          setUser(userData);
        } catch (error) {
          console.error('[Auth] Failed to restore session', error);
          removeAuthToken();
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();

    // Subscribe to forced logout events from the interceptor
    const unsubscribe = eventBus.subscribe('auth:forced_logout' as any, () => {
      handleLogout();
    });

    return () => unsubscribe();
  }, []);

  const handleLogin = async (credentials: LoginCredentials) => {
    const response = await AuthRepository.login(credentials);
    setAuthToken(response.accessToken);

    // We would normally securely store refreshToken as well, perhaps in an HttpOnly cookie or secure storage.
    // For this mock, we'll store it in localStorage for demonstration.
    localStorage.setItem('counterguard_refresh_token', response.refreshToken);

    setUser(response.user);
  };

  const handleLogout = async () => {
    try {
      if (getAuthToken()) {
        await AuthRepository.logout();
      }
    } catch (e) {
      console.warn('[Auth] Logout API failed, proceeding with local clear');
    } finally {
      removeAuthToken();
      localStorage.removeItem('counterguard_refresh_token');
      setUser(null);
      queryClient.clear(); // Clear TanStack Query cache
    }
  };

  const handleRefresh = async () => {
    const refreshToken = localStorage.getItem('counterguard_refresh_token');
    if (!refreshToken) throw new Error('No refresh token available');

    const response = await AuthRepository.refresh(refreshToken);
    setAuthToken(response.accessToken);
    localStorage.setItem('counterguard_refresh_token', response.refreshToken);
    setUser(response.user);
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      isLoading,
      login: handleLogin,
      logout: handleLogout,
      refreshSession: handleRefresh
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

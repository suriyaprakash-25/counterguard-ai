import { apiClient, endpoints } from '../../shared/api';
import { AuthResponse, LoginCredentials, User } from './models';

export const AuthRepository = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const { data } = await apiClient.post(endpoints.auth.login, credentials);
    return data.data;
  },

  async logout(): Promise<void> {
    await apiClient.post(endpoints.auth.logout);
  },

  async refresh(refreshToken: string): Promise<AuthResponse> {
    // We send refreshToken in the body or header depending on backend.
    // For this mock we send it in body.
    const { data } = await apiClient.post(endpoints.auth.refresh, { refreshToken });
    return data.data;
  },

  async getMe(): Promise<User> {
    const { data } = await apiClient.get(endpoints.auth.me);
    return data.data;
  }
};

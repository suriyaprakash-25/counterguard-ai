import axios, { type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios';
import { NetworkError, TimeoutError, UnauthorizedError, ValidationError, UnknownApiError } from './errors';
import { getAuthToken, setAuthToken } from './auth';
import { eventBus } from '../../events/eventBus';

// Extend config to store request start time and retry flag
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
    _retry?: boolean;
  }
}

let isRefreshing = false;
let failedQueue: { resolve: (token: string) => void; reject: (error: any) => void }[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

export const requestInterceptor = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  config.metadata = { startTime: Date.now() };
  config.headers['X-Correlation-ID'] = crypto.randomUUID();

  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
};

export const responseInterceptor = (response: AxiosResponse): AxiosResponse => {
  if (response.config.metadata) {
    const duration = Date.now() - response.config.metadata.startTime;
    if (import.meta.env.DEV) {
      console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
  }
  return response;
};

export const errorInterceptor = async (error: AxiosError): Promise<any> => {
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    return Promise.reject(new TimeoutError());
  }

  if (!error.response) {
    return Promise.reject(new NetworkError());
  }

  const originalRequest = error.config as InternalAxiosRequestConfig;
  const { status, data } = error.response as any;
  const message = data?.error?.message || error.message;
  const details = data?.error?.details;

  // Handle Token Expiration
  if (status === 401 && !originalRequest._retry) {
    if (isRefreshing) {
      return new Promise(function(resolve, reject) {
        failedQueue.push({ resolve, reject });
      }).then(token => {
        originalRequest.headers.Authorization = 'Bearer ' + token;
        return axios(originalRequest);
      }).catch(err => {
        return Promise.reject(err);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const refreshToken = localStorage.getItem('counterguard_refresh_token');
      if (!refreshToken) throw new Error('No refresh token available');

      // Use a raw axios call to avoid interceptor loops
      const baseURL = import.meta.env.VITE_API_BASE_URL || '';
      const response = await axios.post(`${baseURL}/api/v1/auth/refresh`, { refreshToken });

      const newAuthToken = response.data.data.accessToken;
      const newRefreshToken = response.data.data.refreshToken;

      setAuthToken(newAuthToken);
      localStorage.setItem('counterguard_refresh_token', newRefreshToken);

      processQueue(null, newAuthToken);

      originalRequest.headers.Authorization = `Bearer ${newAuthToken}`;
      return axios(originalRequest);
    } catch (err) {
      processQueue(err, null);
      // Fire logout event so AuthProvider clears context and TanStack Query
      eventBus.publish('auth:forced_logout', undefined);
      return Promise.reject(new UnauthorizedError('Session expired. Please log in again.'));
    } finally {
      isRefreshing = false;
    }
  }

  switch (status) {
    case 401:
      return Promise.reject(new UnauthorizedError(message));
    case 422:
    case 400:
      return Promise.reject(new ValidationError(message, details));
    default:
      return Promise.reject(new UnknownApiError(message));
  }
};

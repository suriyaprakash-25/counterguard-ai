import type { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { NetworkError, TimeoutError, UnauthorizedError, ValidationError, UnknownApiError } from './errors';

// Extend config to store request start time
declare module 'axios' {
  export interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

export const requestInterceptor = (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
  // Add timing metadata
  config.metadata = { startTime: Date.now() };

  // Add correlation ID for request tracing
  config.headers['X-Correlation-ID'] = crypto.randomUUID();

  // Future: Add Authentication Token here
  // const token = getAuthToken();
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`;
  // }

  return config;
};

export const responseInterceptor = (response: AxiosResponse): AxiosResponse => {
  // Calculate and log request duration
  if (response.config.metadata) {
    const duration = Date.now() - response.config.metadata.startTime;
    if (import.meta.env.DEV) {
      console.log(`[API] ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
  }

  return response;
};

export const errorInterceptor = (error: AxiosError): Promise<never> => {
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    return Promise.reject(new TimeoutError());
  }

  if (!error.response) {
    return Promise.reject(new NetworkError());
  }

  const { status, data } = error.response as any;
  const message = data?.error?.message || error.message;
  const details = data?.error?.details;

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

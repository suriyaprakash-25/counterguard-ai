import axios from 'axios';
import { requestInterceptor, responseInterceptor, errorInterceptor } from './interceptors';

// Fallback to empty string for relative paths if not configured
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';
const TIMEOUT = 15000; // 15 seconds

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Attach Interceptors
apiClient.interceptors.request.use(requestInterceptor, Promise.reject);
apiClient.interceptors.response.use(responseInterceptor, errorInterceptor);

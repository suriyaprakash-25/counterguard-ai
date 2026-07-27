import { describe, it, expect, vi } from 'vitest';
import { errorInterceptor, requestInterceptor, responseInterceptor } from '../interceptors';
import { NetworkError, TimeoutError, UnauthorizedError, ValidationError, UnknownApiError } from '../errors';

describe('API Interceptors', () => {
  it('adds correlation ID and timestamp in request interceptor', () => {
    const config = { headers: {} } as any;
    const result = requestInterceptor(config);
    expect(result.metadata?.startTime).toBeDefined();
    expect(result.headers['X-Correlation-ID']).toBeDefined();
  });

  it('calculates duration in response interceptor', () => {
    const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
    const response = {
      config: {
        method: 'get',
        url: '/test',
        metadata: { startTime: Date.now() - 100 }
      }
    } as any;

    // Simulate import.meta.env.DEV
    const originalDev = import.meta.env.DEV;
    (import.meta as any).env = { DEV: true };

    responseInterceptor(response);

    expect(spy).toHaveBeenCalled();
    (import.meta as any).env = { DEV: originalDev };
    spy.mockRestore();
  });

  describe('errorInterceptor', () => {
    it('handles timeout errors', async () => {
      const error = { code: 'ECONNABORTED', message: 'timeout' } as any;
      await expect(errorInterceptor(error)).rejects.toThrow(TimeoutError);
    });

    it('handles network errors', async () => {
      const error = { message: 'Network Error' } as any;
      await expect(errorInterceptor(error)).rejects.toThrow(NetworkError);
    });

    it('handles 401 Unauthorized', async () => {
      const error = { message: 'Unauthorized', response: { status: 401 } } as any;
      await expect(errorInterceptor(error)).rejects.toThrow(UnauthorizedError);
    });

    it('handles 422 Validation Error', async () => {
      const error = { message: 'Validation', response: { status: 422, data: { error: { message: 'Invalid', details: {} } } } } as any;
      await expect(errorInterceptor(error)).rejects.toThrow(ValidationError);
    });

    it('handles unknown errors', async () => {
      const error = { message: 'Unknown', response: { status: 500 } } as any;
      await expect(errorInterceptor(error)).rejects.toThrow(UnknownApiError);
    });
  });
});

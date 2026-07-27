export class ApiError extends Error {
  public statusCode: number;
  public code: string;
  public details?: any;

  constructor(message: string, statusCode: number, code: string = 'API_ERROR', details?: any) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

export class NetworkError extends ApiError {
  constructor(message: string = 'Network error occurred. Please check your connection.') {
    super(message, 0, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

export class ValidationError extends ApiError {
  constructor(message: string, details?: any) {
    super(message, 422, 'VALIDATION_ERROR', details);
    this.name = 'ValidationError';
  }
}

export class UnauthorizedError extends ApiError {
  constructor(message: string = 'Unauthorized. Please authenticate.') {
    super(message, 401, 'UNAUTHORIZED');
    this.name = 'UnauthorizedError';
  }
}

export class TimeoutError extends ApiError {
  constructor(message: string = 'Request timed out.') {
    super(message, 408, 'TIMEOUT_ERROR');
    this.name = 'TimeoutError';
  }
}

export class UnknownApiError extends ApiError {
  constructor(message: string = 'An unknown error occurred.') {
    super(message, 500, 'UNKNOWN_ERROR');
    this.name = 'UnknownApiError';
  }
}

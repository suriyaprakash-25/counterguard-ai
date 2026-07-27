export interface ApiResponse<T> {
  data: T;
  meta?: {
    timestamp: string;
    correlationId: string;
    [key: string]: any;
  };
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: any;
  };
}

export interface PaginationResponse<T> extends ApiResponse<T> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface CursorResponse<T> extends ApiResponse<T> {
  cursor: {
    next: string | null;
    prev: string | null;
  };
}

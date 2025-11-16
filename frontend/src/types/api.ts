// API response types

import type { Timestamp } from './base';

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  limit: number;
  offset: number;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
  timestamp: Timestamp;
  request_id?: string;
}

export interface ValidationErrorDetail {
  field: string;
  error: string;
}

export interface ValidationErrorResponse extends ErrorResponse {
  error: 'validation_error';
  details: ValidationErrorDetail[];
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  version: string;
  timestamp: Timestamp;
  services: {
    database: 'connected' | 'disconnected';
    redis: 'connected' | 'disconnected';
    mlflow: 'connected' | 'disconnected';
    lm_studio: 'connected' | 'disconnected';
    docker: 'available' | 'unavailable';
  };
  config_mode: string;
  errors?: string[];
}

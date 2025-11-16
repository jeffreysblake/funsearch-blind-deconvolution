// API Client - Base HTTP client with axios

import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import type { ErrorResponse } from '@/types';

// Get base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:7351';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add any request modifications here (e.g., auth tokens)
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError<ErrorResponse>) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error
      const errorData = error.response.data;
      console.error('API Error:', errorData);

      // You can handle specific error codes here
      if (error.response.status === 401) {
        // Handle unauthorized
      } else if (error.response.status === 404) {
        // Handle not found
      }

      return Promise.reject(errorData);
    } else if (error.request) {
      // Request was made but no response received
      console.error('Network Error:', error.message);
      return Promise.reject({
        error: 'network_error',
        message: 'Unable to connect to the server. Please check your connection.',
      });
    } else {
      // Something else happened
      console.error('Error:', error.message);
      return Promise.reject({
        error: 'unknown_error',
        message: error.message,
      });
    }
  }
);

export default apiClient;

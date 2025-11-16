// Health check API

import apiClient from './client';
import type { HealthResponse } from '@/types';

export const healthApi = {
  // Check system health
  check: async (): Promise<HealthResponse> => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

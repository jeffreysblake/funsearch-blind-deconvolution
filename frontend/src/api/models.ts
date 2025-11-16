// Models (LLM) API

import apiClient from './client';
import type { ModelListResponse } from '@/types';

export const modelsApi = {
  // List available models
  list: async (): Promise<ModelListResponse> => {
    const response = await apiClient.get('/api/v1/models');
    return response.data;
  },
};

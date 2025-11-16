// Templates API

import apiClient from './client';
import type { TemplateDetail, TemplateListResponse } from '@/types';

export const templatesApi = {
  // List all templates
  list: async (): Promise<TemplateListResponse> => {
    const response = await apiClient.get('/api/v1/templates');
    return response.data;
  },

  // Get template by ID
  get: async (templateId: string): Promise<TemplateDetail> => {
    const response = await apiClient.get(`/api/v1/templates/${templateId}`);
    return response.data;
  },
};

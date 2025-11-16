// Projects API

import apiClient from './client';
import type {
  Project,
  ProjectDetail,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectListResponse,
} from '@/types';

export const projectsApi = {
  // List all projects
  list: async (params?: {
    status?: string;
    sort?: string;
    order?: 'asc' | 'desc';
    limit?: number;
    offset?: number;
  }): Promise<ProjectListResponse> => {
    const response = await apiClient.get('/api/v1/projects', { params });
    return response.data;
  },

  // Get project by ID
  get: async (id: string): Promise<ProjectDetail> => {
    const response = await apiClient.get(`/api/v1/projects/${id}`);
    return response.data;
  },

  // Create new project
  create: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post('/api/v1/projects', data);
    return response.data;
  },

  // Update project
  update: async (id: string, data: UpdateProjectRequest): Promise<Project> => {
    const response = await apiClient.patch(`/api/v1/projects/${id}`, data);
    return response.data;
  },

  // Delete project
  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/projects/${id}`);
  },

  // Export project
  export: async (id: string): Promise<{ download_url: string }> => {
    const response = await apiClient.get(`/api/v1/projects/${id}/export`);
    return response.data;
  },
};

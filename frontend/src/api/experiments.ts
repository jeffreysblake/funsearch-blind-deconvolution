// Experiments API

import apiClient from './client';
import type {
  Experiment,
  ExperimentDetail,
  CreateExperimentRequest,
  ExperimentListResponse,
  MetricsTimeSeries,
  IslandState,
} from '@/types';

export const experimentsApi = {
  // List experiments for a project
  list: async (
    projectId: string,
    params?: {
      status?: string;
      limit?: number;
      offset?: number;
    }
  ): Promise<ExperimentListResponse> => {
    const response = await apiClient.get(
      `/api/v1/projects/${projectId}/experiments`,
      { params }
    );
    return response.data;
  },

  // Get experiment by ID
  get: async (experimentId: string): Promise<ExperimentDetail> => {
    const response = await apiClient.get(`/api/v1/experiments/${experimentId}`);
    return response.data;
  },

  // Create new experiment
  create: async (
    projectId: string,
    data: CreateExperimentRequest
  ): Promise<Experiment> => {
    const response = await apiClient.post(
      `/api/v1/projects/${projectId}/experiments`,
      data
    );
    return response.data;
  },

  // Stop experiment
  stop: async (experimentId: string): Promise<Experiment> => {
    const response = await apiClient.post(
      `/api/v1/experiments/${experimentId}/stop`
    );
    return response.data;
  },

  // Pause experiment
  pause: async (experimentId: string): Promise<Experiment> => {
    const response = await apiClient.post(
      `/api/v1/experiments/${experimentId}/pause`
    );
    return response.data;
  },

  // Resume experiment
  resume: async (experimentId: string): Promise<Experiment> => {
    const response = await apiClient.post(
      `/api/v1/experiments/${experimentId}/resume`
    );
    return response.data;
  },

  // Get experiment metrics
  getMetrics: async (
    experimentId: string,
    params?: {
      from_iteration?: number;
      to_iteration?: number;
      interval?: number;
    }
  ): Promise<{ experiment_id: string; metrics: MetricsTimeSeries }> => {
    const response = await apiClient.get(
      `/api/v1/experiments/${experimentId}/metrics`,
      { params }
    );
    return response.data;
  },

  // Get island states
  getIslands: async (
    experimentId: string
  ): Promise<{ experiment_id: string; timestamp: string; islands: IslandState[] }> => {
    const response = await apiClient.get(
      `/api/v1/experiments/${experimentId}/islands`
    );
    return response.data;
  },
};

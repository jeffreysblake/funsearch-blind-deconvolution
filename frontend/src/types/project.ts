// Project-related types

import type { BaseModel } from './base';
import type { Experiment } from './experiment';

export const ProjectStatus = {
  DRAFT: 'draft',
  ACTIVE: 'active',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  ARCHIVED: 'archived',
} as const;

export type ProjectStatus = typeof ProjectStatus[keyof typeof ProjectStatus];

export interface Project extends BaseModel {
  name: string;
  description: string | null;
  problem_type: string;
  status: ProjectStatus;
  spec_file_path: string;
  experiment_count: number;
  best_score: number | null;
}

export interface ProjectDetail extends Project {
  experiments: Experiment[];
  config: Record<string, any>;
}

export interface CreateProjectRequest {
  name: string;
  description?: string;
  problem_type: string;
  template?: string;
  specification: {
    file_content: string;
    evolve_function: string;
    evaluate_function: string;
  };
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: ProjectStatus;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
  limit: number;
  offset: number;
}

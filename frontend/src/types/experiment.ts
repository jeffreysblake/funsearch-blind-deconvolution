// Experiment-related types

import type { UUID, Timestamp } from './base';
import type { MetricsTimeSeries, IslandState } from './metrics';

export const ExperimentStatus = {
  PENDING: 'pending',
  RUNNING: 'running',
  PAUSED: 'paused',
  COMPLETED: 'completed',
  FAILED: 'failed',
  STOPPED: 'stopped',
} as const;

export type ExperimentStatus = typeof ExperimentStatus[keyof typeof ExperimentStatus];

export interface LLMConfig {
  provider: 'lm_studio' | 'mock' | 'template_mock';
  model: string;
  base_url: string;
  temperature: number;
  max_tokens: number;
  timeout: number;
}

export interface SandboxConfig {
  provider: 'docker' | 'subprocess' | 'mock';
  max_workers: number;
  timeout: number;
  image: string;
  limits: {
    memory: string;
    cpu_cores: number;
  };
}

export interface FunSearchConfig {
  samples_per_prompt: number;
  num_islands: number;
  reset_period: number;
  cluster_sampling_temperature_init: number;
  cluster_sampling_temperature_period: number;
}

export interface ExecutionConfig {
  max_iterations: number;
  checkpoint_interval: number;
  log_level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
}

export interface ExperimentConfig {
  llm: LLMConfig;
  sandbox: SandboxConfig;
  funsearch: FunSearchConfig;
  execution: ExecutionConfig;
}

export interface Experiment {
  id: UUID;
  project_id: UUID;
  name: string;
  status: ExperimentStatus;
  config: ExperimentConfig;
  started_at: Timestamp | null;
  completed_at: Timestamp | null;
  paused_at: Timestamp | null;
  iterations_completed: number;
  best_score: number | null;
  mlflow_run_id: string | null;
  task_id: string | null;
}

export interface ExperimentDetail extends Experiment {
  current_score: number | null;
  best_program: string | null;
  metrics: MetricsTimeSeries | null;
  island_states: IslandState[];
  error_message: string | null;
}

export interface CreateExperimentRequest {
  name: string;
  config: ExperimentConfig;
}

export interface ExperimentListResponse {
  experiments: Experiment[];
  total: number;
}

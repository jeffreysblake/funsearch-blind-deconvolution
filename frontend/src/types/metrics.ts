// Metrics and monitoring types

import type { UUID, Timestamp } from './base';

export interface MetricPoint {
  iteration: number;
  timestamp: Timestamp;
  best_score: number;
  avg_score: number | null;
  diversity: number | null;
  samples_generated: number | null;
  successful_evaluations: number | null;
}

export interface MetricsTimeSeries {
  iterations: number[];
  best_score: number[];
  avg_score: number[];
  diversity: number[];
  samples_generated: number[];
  successful_evaluations: number[];
}

export interface Program {
  id: UUID;
  score: number | null;
  code: string;
  signature: string | null;
  created_at: Timestamp;
}

export interface IslandState {
  island_id: number;
  population_size: number;
  best_score: number;
  avg_score: number | null;
  worst_score: number | null;
  diversity: number | null;
  num_clusters: number | null;
  timestamp: Timestamp;
  top_programs: Program[];
}

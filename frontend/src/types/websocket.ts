// WebSocket message types

import type { Timestamp } from './base';
import type { MetricPoint } from './metrics';
import type { ExperimentStatus } from './experiment';

export type WSMessageType =
  | 'subscribe'
  | 'unsubscribe'
  | 'ping'
  | 'pong'
  | 'metrics_update'
  | 'island_update'
  | 'best_program_update'
  | 'log'
  | 'status_change'
  | 'error';

export interface WSMessage {
  type: WSMessageType;
  timestamp: Timestamp;
}

export interface WSSubscribe extends WSMessage {
  type: 'subscribe';
  channels: string[];
}

export interface WSUnsubscribe extends WSMessage {
  type: 'unsubscribe';
  channels: string[];
}

export interface WSPing extends WSMessage {
  type: 'ping';
}

export interface WSPong extends WSMessage {
  type: 'pong';
}

export interface WSMetricsUpdate extends WSMessage {
  type: 'metrics_update';
  data: MetricPoint;
}

export interface WSBestProgramUpdate extends WSMessage {
  type: 'best_program_update';
  data: {
    iteration: number;
    score: number;
    previous_score: number;
    improvement: number;
    code: string;
  };
}

export interface WSIslandUpdate extends WSMessage {
  type: 'island_update';
  data: {
    island_id: number;
    best_score: number;
    population_size: number;
    diversity: number;
  };
}

export interface WSStatusChange extends WSMessage {
  type: 'status_change';
  old_status: ExperimentStatus;
  new_status: ExperimentStatus;
  reason?: string;
}

export interface WSError extends WSMessage {
  type: 'error';
  error_code: string;
  message: string;
  details?: Record<string, any>;
}

export interface WSLogMessage extends WSMessage {
  type: 'log';
  level: 'debug' | 'info' | 'warning' | 'error';
  message: string;
}

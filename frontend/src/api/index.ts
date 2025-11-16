// API exports

export { default as apiClient } from './client';
export * from './projects';
export * from './experiments';
export * from './models';
export * from './templates';
export * from './health';

import { projectsApi } from './projects';
import { experimentsApi } from './experiments';
import { modelsApi } from './models';
import { templatesApi } from './templates';
import { healthApi } from './health';

// Re-export for convenience
export const api = {
  projects: projectsApi,
  experiments: experimentsApi,
  models: modelsApi,
  templates: templatesApi,
  health: healthApi,
} as const;

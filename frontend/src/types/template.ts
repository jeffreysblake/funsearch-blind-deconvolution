// Project template types

import type { ExperimentConfig } from './experiment';

export interface TemplateInfo {
  id: string;
  name: string;
  description: string;
  example_problems: string[];
}

export interface TemplateDetail extends TemplateInfo {
  specification_template: string;
  default_config: ExperimentConfig;
  example: Record<string, any>;
}

export interface TemplateListResponse {
  templates: TemplateInfo[];
}

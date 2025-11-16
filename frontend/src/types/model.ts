// LLM Model types

export interface ModelInfo {
  id: string;
  name: string;
  size?: string;
  type?: string;
  loaded: boolean;
}

export interface ModelListResponse {
  models: ModelInfo[];
  provider: string;
  base_url: string;
}

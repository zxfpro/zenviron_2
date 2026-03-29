export type ProviderName = "openai" | "anthropic" | "deepseek" | "qwen";

export interface ProviderProfile {
  provider: ProviderName;
  enabled: boolean;
  base_url: string;
  api_key: string;
  alias: string;
  model: string;
  timeout: number;
  max_tokens: number;
  temperature: number;
  note: string;
}

export interface LLMConfig {
  meta: {
    version: number;
    updated_at: string;
    active_alias: string;
  };
  profiles: Record<string, ProviderProfile>;
}

export interface ConfigEnvelope {
  config: LLMConfig;
  version_hash: string;
}

export interface StreamPayload {
  event: string;
  version_hash: string;
  alias?: string;
}

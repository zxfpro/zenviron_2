import type { ConfigEnvelope, ProviderProfile, StreamPayload } from "../types/config";

const jsonHeaders = { "Content-Type": "application/json" };

export async function fetchConfig(): Promise<ConfigEnvelope> {
  const res = await fetch("/api/v1/llm-config");
  if (!res.ok) throw new Error("Failed to load config");
  return res.json();
}

export async function saveConfig(config: ConfigEnvelope): Promise<ConfigEnvelope> {
  const res = await fetch("/api/v1/llm-config", {
    method: "PUT",
    headers: jsonHeaders,
    body: JSON.stringify({ config: config.config, base_version_hash: config.version_hash }),
  });
  if (res.status === 409) throw new Error("CONFLICT");
  if (!res.ok) throw new Error("Failed to save config");
  return res.json();
}

export async function patchProfile(
  alias: string,
  profile: ProviderProfile,
  versionHash: string,
  sourceAlias?: string,
): Promise<ConfigEnvelope> {
  const sourceAliasQuery = sourceAlias ? `?source_alias=${encodeURIComponent(sourceAlias)}` : "";
  const res = await fetch(`/api/v1/llm-config/profiles/${encodeURIComponent(alias)}${sourceAliasQuery}`, {
    method: "PATCH",
    headers: jsonHeaders,
    body: JSON.stringify({ profile, base_version_hash: versionHash }),
  });
  if (res.status === 409) throw new Error("CONFLICT");
  if (!res.ok) throw new Error("Failed to patch profile");
  return res.json();
}

export async function setActiveAlias(alias: string, versionHash: string): Promise<ConfigEnvelope> {
  const res = await fetch(`/api/v1/llm-config/active/${encodeURIComponent(alias)}?base_version_hash=${encodeURIComponent(versionHash)}`, {
    method: "POST",
  });
  if (res.status === 409) throw new Error("CONFLICT");
  if (!res.ok) throw new Error("Failed to switch active model");
  return res.json();
}

export async function deleteProfile(alias: string, versionHash: string): Promise<ConfigEnvelope> {
  const res = await fetch(
    `/api/v1/llm-config/profiles/${encodeURIComponent(alias)}?base_version_hash=${encodeURIComponent(versionHash)}`,
    { method: "DELETE" },
  );
  if (res.status === 409) throw new Error("CONFLICT");
  if (!res.ok) throw new Error("Failed to delete profile");
  return res.json();
}

export async function testProfile(alias: string): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`/api/v1/llm-config/profiles/${encodeURIComponent(alias)}/test`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to test profile");
  return res.json();
}

export function subscribeConfigEvents(onMessage: (evt: StreamPayload) => void): () => void {
  const source = new EventSource("/api/v1/llm-config/stream");
  source.onmessage = (event) => {
    try {
      onMessage(JSON.parse(event.data) as StreamPayload);
    } catch {
      // Ignore malformed messages.
    }
  };
  return () => source.close();
}

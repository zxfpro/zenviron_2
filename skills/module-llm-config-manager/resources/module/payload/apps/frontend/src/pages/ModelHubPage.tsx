import { useEffect, useMemo, useState } from "react";
import { testProfile } from "../services/configApi";
import type { ConfigEnvelope, ProviderProfile } from "../types/config";

interface Props {
  envelope: ConfigEnvelope | null;
  externalChanged: boolean;
  onUpsertProfile: (alias: string, value: ProviderProfile, sourceAlias?: string) => Promise<void>;
}

export function ModelHubPage({ envelope, externalChanged, onUpsertProfile }: Props) {
  const [selectedAlias, setSelectedAlias] = useState<string>("");
  const [draft, setDraft] = useState<ProviderProfile | null>(null);
  const [showApiKey, setShowApiKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState<string>("");

  const aliases = useMemo(() => Object.keys(envelope?.config.profiles ?? {}), [envelope]);

  useEffect(() => {
    if (!selectedAlias && aliases.length > 0) {
      setSelectedAlias(aliases[0]);
    }
    if (selectedAlias && !aliases.includes(selectedAlias) && aliases.length > 0) {
      setSelectedAlias(aliases[0]);
    }
  }, [aliases, selectedAlias]);

  const selectedProfile = selectedAlias && envelope ? envelope.config.profiles[selectedAlias] : null;
  const activeProfile = draft ?? selectedProfile;

  function selectAlias(alias: string) {
    setSelectedAlias(alias);
    setDraft(null);
    setTestResult("");
  }

  async function onSave() {
    if (!activeProfile) return;
    const alias = activeProfile.alias.trim();
    if (!alias) return;
    setSaving(true);
    try {
      await onUpsertProfile(alias, { ...activeProfile, alias }, selectedAlias || undefined);
      setSelectedAlias(alias);
      setDraft(null);
    } finally {
      setSaving(false);
    }
  }

  async function onTest() {
    if (!activeProfile) return;
    const alias = activeProfile.alias.trim();
    if (!alias) return;
    const res = await testProfile(alias);
    setTestResult(`${alias}: ${res.message}`);
  }

  if (!envelope || !activeProfile) {
    return (
      <main className="page">
        <div className="page-title">
          <h2>LLM 首选项</h2>
          <p>加载配置中...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="page-title">
        <h2>LLM 首选项</h2>
        <p>支持同一 Provider 下多个方案，Alias 作为唯一 ID。</p>
      </div>

      {externalChanged ? <div className="alert">检测到 TOML 外部更新，页面数据已刷新。</div> : null}
      {testResult ? <div className="alert neutral">{testResult}</div> : null}

      <section className="provider-config-panel">
        <h3>配置方案</h3>
        <div className="provider-summary">
          <strong>{activeProfile.provider.toUpperCase()}</strong>
        </div>

        <div className="configured-model-select">
          <label className="field">
            <span>已配好的模型</span>
            <select value={selectedAlias} onChange={(e) => selectAlias(e.target.value)}>
              {aliases.map((alias) => (
                <option key={alias} value={alias}>
                  {alias} ({envelope.config.profiles[alias].model || "未设置模型"})
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="config-grid">
          <label className="field">
            <span>Alias (唯一ID)</span>
            <input
              value={activeProfile.alias}
              onChange={(e) => setDraft({ ...activeProfile, alias: e.target.value })}
              placeholder="openai_default"
            />
          </label>
          <label className="field">
            <span>Provider</span>
            <input value={activeProfile.provider.toUpperCase()} readOnly />
          </label>
          <label className="field">
            <span>Base URL</span>
            <input
              value={activeProfile.base_url}
              onChange={(e) => setDraft({ ...activeProfile, base_url: e.target.value })}
              placeholder="https://api.example.com/v1"
            />
          </label>
          <label className="field">
            <span>API Key</span>
            <div className="inline-input">
              <input
                type={showApiKey ? "text" : "password"}
                value={activeProfile.api_key}
                onChange={(e) => setDraft({ ...activeProfile, api_key: e.target.value })}
                placeholder="sk-..."
              />
              <button type="button" onClick={() => setShowApiKey((v) => !v)}>
                {showApiKey ? "隐藏" : "显示"}
              </button>
            </div>
          </label>
          <label className="field">
            <span>Chat Model Name</span>
            <input
              value={activeProfile.model}
              onChange={(e) => setDraft({ ...activeProfile, model: e.target.value })}
              placeholder="gpt-5.4-2026-03-05"
            />
          </label>
          <label className="field">
            <span>Max Tokens</span>
            <input
              type="number"
              value={activeProfile.max_tokens}
              onChange={(e) => setDraft({ ...activeProfile, max_tokens: Number(e.target.value) })}
            />
          </label>
        </div>

        <div className="toggle-row">
          <label>
            <input
              type="checkbox"
              checked={activeProfile.enabled}
              onChange={(e) => setDraft({ ...activeProfile, enabled: e.target.checked })}
            />
            启用该方案
          </label>
        </div>

        <div className="panel-actions">
          <button type="button" onClick={onTest}>
            测试连接
          </button>
          <button type="button" onClick={onSave} disabled={saving}>
            {saving ? "保存中..." : "保存方案"}
          </button>
        </div>
      </section>
    </main>
  );
}

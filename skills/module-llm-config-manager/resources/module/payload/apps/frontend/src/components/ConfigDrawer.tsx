import { useState } from "react";
import type { ProviderConfig, ProviderName } from "../types/config";

interface Props {
  providerName: ProviderName;
  config: ProviderConfig;
  externalChanged: boolean;
  onClose: () => void;
  onSave: (value: ProviderConfig) => Promise<void>;
}

export function ConfigDrawer({ providerName, config, externalChanged, onClose, onSave }: Props) {
  const [draft, setDraft] = useState<ProviderConfig>(config);
  const [saving, setSaving] = useState(false);

  async function submit() {
    setSaving(true);
    try {
      await onSave(draft);
      onClose();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="drawer-overlay">
      <div className="drawer">
        <h3>{providerName.toUpperCase()} Config</h3>
        {externalChanged ? <p className="warning">文件已外部更新，保存前请确认字段。</p> : null}
        <label>
          <input
            type="checkbox"
            checked={draft.enabled}
            onChange={(e) => setDraft({ ...draft, enabled: e.target.checked })}
          />
          Enabled
        </label>
        <input value={draft.base_url} onChange={(e) => setDraft({ ...draft, base_url: e.target.value })} placeholder="Base URL" />
        <input value={draft.model} onChange={(e) => setDraft({ ...draft, model: e.target.value })} placeholder="Model" />
        <input
          type="number"
          value={draft.temperature}
          onChange={(e) => setDraft({ ...draft, temperature: Number(e.target.value) })}
          placeholder="Temperature"
        />
        <input
          type="number"
          value={draft.max_tokens}
          onChange={(e) => setDraft({ ...draft, max_tokens: Number(e.target.value) })}
          placeholder="Max Tokens"
        />
        <input
          type="number"
          value={draft.timeout}
          onChange={(e) => setDraft({ ...draft, timeout: Number(e.target.value) })}
          placeholder="Timeout"
        />
        <textarea value={draft.note} onChange={(e) => setDraft({ ...draft, note: e.target.value })} placeholder="Note" />

        <div className="drawer-actions">
          <button onClick={onClose}>Cancel</button>
          <button onClick={submit} disabled={saving}>{saving ? "Saving..." : "Save"}</button>
        </div>
      </div>
    </div>
  );
}

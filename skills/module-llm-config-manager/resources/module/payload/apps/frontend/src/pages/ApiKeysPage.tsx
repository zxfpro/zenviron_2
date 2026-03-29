import type { ConfigEnvelope } from "../types/config";

interface Props {
  envelope: ConfigEnvelope | null;
  onSetActiveAlias: (alias: string) => Promise<void>;
  onDeleteProfile: (alias: string) => Promise<void>;
}

function mask(key: string): string {
  if (!key) return "(empty)";
  if (key.length <= 8) return "*".repeat(key.length);
  return `${key.slice(0, 4)}${"*".repeat(Math.max(4, key.length - 8))}${key.slice(-4)}`;
}

export function ApiKeysPage({ envelope, onSetActiveAlias, onDeleteProfile }: Props) {
  if (!envelope) return <main className="page">Loading...</main>;

  const rows = Object.entries(envelope.config.profiles).map(([alias, profile]) => ({ alias, profile }));
  const canDelete = rows.length > 1;

  async function handleDelete(alias: string) {
    if (!canDelete) return;
    if (!window.confirm(`确认删除方案 ${alias} 吗？`)) return;
    await onDeleteProfile(alias);
  }

  return (
    <main className="page">
      <div className="page-title">
        <h2>Model Switch</h2>
        <p>展示已存储方案，并按 Alias 勾选切换当前主模型。</p>
      </div>
      <table className="keys-table">
        <thead>
          <tr>
            <th>Active</th>
            <th>Alias (ID)</th>
            <th>Provider</th>
            <th>Model</th>
            <th>Current Key</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(({ alias, profile }) => (
            <tr key={alias}>
              <td>
                <input
                  type="checkbox"
                  checked={envelope.config.meta.active_alias === alias}
                  onChange={() => onSetActiveAlias(alias)}
                />
              </td>
              <td>{alias}</td>
              <td>{profile.provider.toUpperCase()}</td>
              <td>{profile.model || "-"}</td>
              <td>{mask(profile.api_key)}</td>
              <td>{profile.enabled ? "Enabled" : "Disabled"}</td>
              <td>
                <button type="button" onClick={() => void handleDelete(alias)} disabled={!canDelete}>
                  删除
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}

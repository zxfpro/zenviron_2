import { useEffect, useMemo, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { SideNav } from "./components/SideNav";
import { TopAppBar } from "./components/TopAppBar";
import { ApiKeysPage } from "./pages/ApiKeysPage";
import { DashboardPage } from "./pages/DashboardPage";
import { ModelHubPage } from "./pages/ModelHubPage";
import { SettingsPage } from "./pages/SettingsPage";
import { deleteProfile, fetchConfig, patchProfile, setActiveAlias, subscribeConfigEvents } from "./services/configApi";
import type { ConfigEnvelope, ProviderProfile } from "./types/config";

export function App() {
  const [envelope, setEnvelope] = useState<ConfigEnvelope | null>(null);
  const [externalChanged, setExternalChanged] = useState(false);
  const [error, setError] = useState("");

  async function reloadConfig() {
    try {
      const next = await fetchConfig();
      setEnvelope(next);
      setError("");
    } catch (err) {
      setError(String(err));
    }
  }

  async function onUpsertProfile(alias: string, profile: ProviderProfile, sourceAlias?: string) {
    if (!envelope) return;
    try {
      const next = await patchProfile(alias, profile, envelope.version_hash, sourceAlias);
      setEnvelope(next);
      setExternalChanged(false);
    } catch (err) {
      if (String(err).includes("CONFLICT")) {
        setError("配置冲突：文件已被外部更新，请刷新后重试。");
        await reloadConfig();
        return;
      }
      setError(String(err));
    }
  }

  async function onSetActiveAlias(alias: string) {
    if (!envelope) return;
    try {
      const next = await setActiveAlias(alias, envelope.version_hash);
      setEnvelope(next);
      setExternalChanged(false);
    } catch (err) {
      if (String(err).includes("CONFLICT")) {
        setError("配置冲突：文件已被外部更新，请刷新后重试。");
        await reloadConfig();
        return;
      }
      setError(String(err));
    }
  }

  async function onDeleteProfile(alias: string) {
    if (!envelope) return;
    try {
      const next = await deleteProfile(alias, envelope.version_hash);
      setEnvelope(next);
      setExternalChanged(false);
    } catch (err) {
      if (String(err).includes("CONFLICT")) {
        setError("配置冲突：文件已被外部更新，请刷新后重试。");
        await reloadConfig();
        return;
      }
      setError(String(err));
    }
  }

  useEffect(() => {
    void reloadConfig();
    const unsubscribe = subscribeConfigEvents(async () => {
      setExternalChanged(true);
      await reloadConfig();
    });
    return unsubscribe;
  }, []);

  const content = useMemo(() => {
    if (error) return <div className="error-banner">{error}</div>;
    return null;
  }, [error]);

  return (
    <div className="layout">
      <TopAppBar />
      <div className="body-area">
        <SideNav />
        <section className="content-area">
          {content}
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route
              path="/hub"
              element={
                <ModelHubPage
                  envelope={envelope}
                  externalChanged={externalChanged}
                  onUpsertProfile={onUpsertProfile}
                />
              }
            />
            <Route
              path="/keys"
              element={
                <ApiKeysPage
                  envelope={envelope}
                  onSetActiveAlias={onSetActiveAlias}
                  onDeleteProfile={onDeleteProfile}
                />
              }
            />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </section>
      </div>
    </div>
  );
}

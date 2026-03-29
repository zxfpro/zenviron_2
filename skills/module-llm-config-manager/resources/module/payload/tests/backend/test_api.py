from pathlib import Path

from fastapi.testclient import TestClient


def test_get_and_patch_api(tmp_path: Path, monkeypatch) -> None:
    config_path = tmp_path / "llm_providers.toml"
    monkeypatch.setenv("LLM_CONFIG_PATH", str(config_path))

    from apps.backend.src.main import app

    with TestClient(app) as client:
        get_res = client.get("/api/v1/llm-config")
        assert get_res.status_code == 200

        body = get_res.json()
        version_hash = body["version_hash"]

        patch_res = client.patch(
            "/api/v1/llm-config/profiles/openai_fast",
            json={
                "profile": {
                    "provider": "openai",
                    "enabled": True,
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "sk-new",
                    "alias": "openai_fast",
                    "model": "gpt-4o-mini",
                    "timeout": 30,
                    "max_tokens": 2048,
                    "temperature": 0.8,
                    "note": "patched",
                },
                "base_version_hash": version_hash,
            },
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["config"]["profiles"]["openai_fast"]["api_key"] == "sk-new"

        rename_hash = patch_res.json()["version_hash"]
        rename_res = client.patch(
            "/api/v1/llm-config/profiles/openai_fast_v2?source_alias=openai_fast",
            json={
                "profile": {
                    "provider": "openai",
                    "enabled": True,
                    "base_url": "https://api.openai.com/v1",
                    "api_key": "sk-new",
                    "alias": "openai_fast_v2",
                    "model": "gpt-4o-mini",
                    "timeout": 30,
                    "max_tokens": 2048,
                    "temperature": 0.8,
                    "note": "renamed",
                },
                "base_version_hash": rename_hash,
            },
        )
        assert rename_res.status_code == 200
        assert "openai_fast" not in rename_res.json()["config"]["profiles"]
        assert "openai_fast_v2" in rename_res.json()["config"]["profiles"]

        switch_hash = rename_res.json()["version_hash"]
        set_active_res = client.post(
            f"/api/v1/llm-config/active/openai_fast_v2?base_version_hash={switch_hash}",
        )
        assert set_active_res.status_code == 200
        assert set_active_res.json()["config"]["meta"]["active_alias"] == "openai_fast_v2"

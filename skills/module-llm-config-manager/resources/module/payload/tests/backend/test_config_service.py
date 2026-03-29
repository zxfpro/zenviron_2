from pathlib import Path

from apps.backend.src.config_service import LLMConfigService, VersionConflictError
from apps.backend.src.models import ProviderProfile


def test_read_write_and_hash_changes(tmp_path: Path) -> None:
    config_path = tmp_path / "llm_providers.toml"
    service = LLMConfigService(config_path)

    first = service.get_envelope()
    original_hash = first["version_hash"]

    payload = service.read_config()
    payload.profiles["openai_default"].model = "gpt-4o"

    saved = service.replace_config(payload, original_hash)

    assert saved["config"]["profiles"]["openai_default"]["model"] == "gpt-4o"
    assert saved["version_hash"] != original_hash


def test_version_conflict(tmp_path: Path) -> None:
    config_path = tmp_path / "llm_providers.toml"
    service = LLMConfigService(config_path)

    stale_hash = "stale"
    payload = service.read_config()

    try:
        service.replace_config(payload, stale_hash)
    except VersionConflictError:
        assert True
    else:
        assert False, "expected version conflict"


def test_patch_profile(tmp_path: Path) -> None:
    config_path = tmp_path / "llm_providers.toml"
    service = LLMConfigService(config_path)

    env = service.get_envelope()
    next_profile = ProviderProfile(
        provider="openai",
        enabled=True,
        base_url="https://api.openai.com/v1",
        api_key="sk-test",
        alias="openai_fast",
        model="gpt-4o-mini",
        timeout=20,
        max_tokens=4096,
        temperature=0.3,
        note="updated",
    )

    updated = service.patch_profile("openai_fast", next_profile, env["version_hash"])

    assert updated["config"]["profiles"]["openai_fast"]["api_key"] == "sk-test"
    assert updated["config"]["profiles"]["openai_fast"]["provider"] == "openai"

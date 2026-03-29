from __future__ import annotations

import asyncio
import hashlib
import os
import tempfile
import threading
from pathlib import Path
from typing import Any

import tomli_w
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from .models import LLMConfig, MetaConfig, ProviderProfile

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


DEFAULT_CONFIG = LLMConfig(
    meta=MetaConfig.now(version=1, active_alias="openai_default"),
    profiles={
        "openai_default": ProviderProfile(
            provider="openai",
            enabled=True,
            base_url="https://api.openai.com/v1",
            alias="openai_default",
            model="gpt-4o-mini",
        ),
        "anthropic_default": ProviderProfile(
            provider="anthropic",
            enabled=False,
            base_url="https://api.anthropic.com/v1",
            alias="anthropic_default",
            model="claude-3-5-sonnet-latest",
        ),
    },
)


class VersionConflictError(Exception):
    pass


class LLMConfigService:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self._lock = threading.RLock()
        self._queues: list[asyncio.Queue[dict[str, Any]]] = []
        self._observer: Observer | None = None

    def ensure_initialized(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config_path.exists():
            self._write_config(DEFAULT_CONFIG)

    def get_envelope(self) -> dict[str, Any]:
        config = self.read_config()
        return {
            "config": config.model_dump(),
            "version_hash": self.current_hash(),
        }

    def read_config(self) -> LLMConfig:
        self.ensure_initialized()
        with self._lock:
            data = tomllib.loads(self.config_path.read_text(encoding="utf-8"))
            normalized = self._normalize_legacy_data(data)
            return LLMConfig.model_validate(normalized)

    def replace_config(self, payload: LLMConfig, base_version_hash: str) -> dict[str, Any]:
        with self._lock:
            current = self.current_hash()
            if current != base_version_hash:
                raise VersionConflictError
            payload = self._ensure_alias_integrity(payload)
            active_alias = payload.meta.active_alias
            if active_alias not in payload.profiles and payload.profiles:
                active_alias = next(iter(payload.profiles.keys()))
            payload.meta = MetaConfig.now(
                version=payload.meta.version + 1,
                active_alias=active_alias,
            )
            self._write_config(payload)
            self._publish_change(event="config_replaced")
        return self.get_envelope()

    def patch_profile(
        self,
        alias: str,
        profile: ProviderProfile,
        base_version_hash: str,
        source_alias: str | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            current = self.current_hash()
            if current != base_version_hash:
                raise VersionConflictError
            config = self.read_config()
            if source_alias and source_alias != alias:
                if source_alias not in config.profiles:
                    raise KeyError(source_alias)
                if alias in config.profiles:
                    raise ValueError("target alias already exists")
                del config.profiles[source_alias]
                if config.meta.active_alias == source_alias:
                    config.meta.active_alias = alias
            profile.alias = alias
            config.profiles[alias] = profile
            config = self._ensure_alias_integrity(config)
            active_alias = config.meta.active_alias if config.meta.active_alias in config.profiles else alias
            config.meta = MetaConfig.now(
                version=config.meta.version + 1,
                active_alias=active_alias,
            )
            self._write_config(config)
            self._publish_change(event="profile_patched", alias=alias)
        return self.get_envelope()

    def set_active_alias(self, alias: str, base_version_hash: str) -> dict[str, Any]:
        with self._lock:
            current = self.current_hash()
            if current != base_version_hash:
                raise VersionConflictError
            config = self.read_config()
            if alias not in config.profiles:
                raise KeyError(alias)
            config.meta = MetaConfig.now(version=config.meta.version + 1, active_alias=alias)
            self._write_config(config)
            self._publish_change(event="active_alias_changed", alias=alias)
        return self.get_envelope()

    def delete_profile(self, alias: str, base_version_hash: str) -> dict[str, Any]:
        with self._lock:
            current = self.current_hash()
            if current != base_version_hash:
                raise VersionConflictError
            config = self.read_config()
            if alias not in config.profiles:
                raise KeyError(alias)
            if len(config.profiles) <= 1:
                raise ValueError("cannot delete the last profile")

            del config.profiles[alias]
            next_active_alias = config.meta.active_alias
            if next_active_alias == alias:
                next_active_alias = next(iter(config.profiles.keys()))
            config.meta = MetaConfig.now(version=config.meta.version + 1, active_alias=next_active_alias)
            self._write_config(config)
            self._publish_change(event="profile_deleted", alias=alias)
        return self.get_envelope()

    def current_hash(self) -> str:
        self.ensure_initialized()
        with self._lock:
            payload = self.config_path.read_bytes()
        return hashlib.sha256(payload).hexdigest()

    def _write_config(self, config: LLMConfig) -> None:
        payload = tomli_w.dumps(config.model_dump())
        fd, tmp_path = tempfile.mkstemp(
            prefix="llm_providers_",
            suffix=".toml",
            dir=str(self.config_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_path, self.config_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def register_queue(self) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
        self._queues.append(queue)
        return queue

    def unregister_queue(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        if queue in self._queues:
            self._queues.remove(queue)

    def _publish_change(self, event: str, **kwargs: Any) -> None:
        payload: dict[str, Any] = {
            "event": event,
            "version_hash": self.current_hash(),
        }
        payload.update(kwargs)
        for queue in list(self._queues):
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                continue

    def _normalize_legacy_data(self, data: dict[str, Any]) -> dict[str, Any]:
        if "profiles" in data:
            return data

        providers = data.get("providers", {})
        profiles: dict[str, dict[str, Any]] = {}
        for provider_name, provider_cfg in providers.items():
            alias = provider_cfg.get("alias") or f"{provider_name}_default"
            profiles[alias] = {
                "provider": provider_name,
                "enabled": provider_cfg.get("enabled", False),
                "base_url": provider_cfg.get("base_url", ""),
                "api_key": provider_cfg.get("api_key", ""),
                "alias": alias,
                "model": provider_cfg.get("model", ""),
                "timeout": provider_cfg.get("timeout", 30),
                "max_tokens": provider_cfg.get("max_tokens", 2048),
                "temperature": provider_cfg.get("temperature", 0.7),
                "note": provider_cfg.get("note", ""),
            }

        active_alias = data.get("meta", {}).get("active_alias")
        if not active_alias:
            active_alias = next(iter(profiles.keys()), "openai_default")

        return {
            "meta": {
                "version": data.get("meta", {}).get("version", 1),
                "updated_at": data.get("meta", {}).get("updated_at", ""),
                "active_alias": active_alias,
            },
            "profiles": profiles,
        }

    def _ensure_alias_integrity(self, config: LLMConfig) -> LLMConfig:
        normalized: dict[str, ProviderProfile] = {}
        for alias, profile in config.profiles.items():
            clean_alias = alias.strip()
            if not clean_alias:
                continue
            profile.alias = clean_alias
            normalized[clean_alias] = profile
        config.profiles = normalized
        return config

    def start_file_watch(self) -> None:
        if self._observer:
            return
        handler = _ConfigChangeHandler(self)
        observer = Observer()
        observer.schedule(handler, str(self.config_path.parent), recursive=False)
        observer.start()
        self._observer = observer

    def stop_file_watch(self) -> None:
        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=2)
            self._observer = None


class _ConfigChangeHandler(FileSystemEventHandler):
    def __init__(self, service: LLMConfigService) -> None:
        self.service = service

    def on_modified(self, event) -> None:  # type: ignore[no-untyped-def]
        if Path(event.src_path) == self.service.config_path:
            self.service._publish_change(event="file_changed")

    def on_created(self, event) -> None:  # type: ignore[no-untyped-def]
        if Path(event.src_path) == self.service.config_path:
            self.service._publish_change(event="file_changed")

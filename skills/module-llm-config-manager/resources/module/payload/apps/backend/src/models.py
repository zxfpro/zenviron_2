from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

ProviderName = Literal["openai", "anthropic", "deepseek", "qwen"]


class ProviderProfile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: ProviderName = "openai"
    enabled: bool = True
    base_url: str = ""
    api_key: str = ""
    alias: str = ""
    model: str = ""
    timeout: int = Field(default=30, ge=1, le=300)
    max_tokens: int = Field(default=2048, ge=1, le=262144)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    note: str = ""

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        if value and not (value.startswith("http://") or value.startswith("https://")):
            msg = "base_url must start with http:// or https://"
            raise ValueError(msg)
        return value


class MetaConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int = 1
    updated_at: str = ""
    active_alias: str = "openai_default"

    @classmethod
    def now(cls, version: int, active_alias: str = "openai_default") -> "MetaConfig":
        return cls(
            version=version,
            updated_at=datetime.now(timezone.utc).isoformat(),
            active_alias=active_alias,
        )


class LLMConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    meta: MetaConfig
    profiles: dict[str, ProviderProfile]


class ConfigEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config: LLMConfig
    version_hash: str


class PutConfigRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    config: LLMConfig
    base_version_hash: str


class PatchProfileRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    profile: ProviderProfile
    base_version_hash: str

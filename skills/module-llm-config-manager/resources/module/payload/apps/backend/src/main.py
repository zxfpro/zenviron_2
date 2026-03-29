from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .config_service import LLMConfigService, VersionConflictError
from .models import PatchProfileRequest, PutConfigRequest

config_path = Path(os.getenv("LLM_CONFIG_PATH", "config/llm_providers.toml"))
service = LLMConfigService(config_path=config_path)


@asynccontextmanager
async def lifespan(_: FastAPI):
    service.ensure_initialized()
    service.start_file_watch()
    try:
        yield
    finally:
        service.stop_file_watch()


app = FastAPI(title="LLM Config Manager API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/llm-config")
def get_llm_config() -> dict:
    return service.get_envelope()


@app.put("/api/v1/llm-config")
def put_llm_config(payload: PutConfigRequest) -> dict:
    try:
        return service.replace_config(payload.config, payload.base_version_hash)
    except VersionConflictError as exc:
        raise HTTPException(status_code=409, detail="version conflict") from exc


@app.patch("/api/v1/llm-config/profiles/{alias}")
def patch_profile(alias: str, payload: PatchProfileRequest, source_alias: str | None = None) -> dict:
    try:
        return service.patch_profile(alias, payload.profile, payload.base_version_hash, source_alias=source_alias)
    except VersionConflictError as exc:
        raise HTTPException(status_code=409, detail="version conflict") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="source alias not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/llm-config/active/{alias}")
def set_active_alias(alias: str, base_version_hash: str) -> dict:
    try:
        return service.set_active_alias(alias, base_version_hash)
    except VersionConflictError as exc:
        raise HTTPException(status_code=409, detail="version conflict") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="alias not found") from exc


@app.delete("/api/v1/llm-config/profiles/{alias}")
def delete_profile(alias: str, base_version_hash: str) -> dict:
    try:
        return service.delete_profile(alias, base_version_hash)
    except VersionConflictError as exc:
        raise HTTPException(status_code=409, detail="version conflict") from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="alias not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/llm-config/profiles/{alias}/test")
async def test_profile(alias: str) -> dict[str, str | bool]:
    config = service.read_config()
    cfg = config.profiles.get(alias)
    if not cfg:
        return {"success": False, "message": "alias not found"}
    if not cfg.base_url or not cfg.api_key:
        return {"success": False, "message": "missing base_url or api_key"}

    headers = {"Authorization": f"Bearer {cfg.api_key}"}
    target = cfg.base_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=min(cfg.timeout, 10)) as client:
            response = await client.get(target, headers=headers)
        ok = response.status_code < 500
        return {
            "success": ok,
            "message": f"status={response.status_code}",
        }
    except Exception as exc:  # pragma: no cover
        return {
            "success": False,
            "message": f"connection error: {exc}",
        }


@app.get("/api/v1/llm-config/stream")
async def stream_config_events() -> StreamingResponse:
    queue = service.register_queue()

    async def generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\\n\\n"
        finally:
            service.unregister_queue(queue)

    return StreamingResponse(generator(), media_type="text/event-stream")


@app.post("/api/v1/llm-config/reload")
def reload_from_disk() -> dict:
    return service.get_envelope()

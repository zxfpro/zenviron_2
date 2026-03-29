# Integration Spec

## Scope

- Alias-based LLM profile CRUD and switching
- TOML persistence and SSE sync

## Required touchpoints

- Backend app bootstrap and service routing
- Frontend route mount and API proxy
- Config file path and file permissions

## Compatibility notes

- Designed for React + Vite frontend and FastAPI backend.
- If target stack differs, retain API contract and adapt UI/service shell only.

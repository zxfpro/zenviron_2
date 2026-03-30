---
name: project-deploy-ops
description: Handle environment setup, containerized deployment, rollout validation, rollback, and runtime troubleshooting for this project. Use when deploying via Docker Compose, validating nginx routing, checking health endpoints, diagnosing service startup failures, or recovering from bad releases.
---

# Project Deploy Ops

## Deployment Workflow

1. Validate environment variables and secrets presence.
2. Build and start services with explicit compose target.
3. Verify container health, ports, and logs.
4. Verify API and nginx routing with smoke requests.
5. Document rollback command before finishing.

## Operational Rules

- Prefer reproducible, scriptable commands.
- Verify each layer: app, db, reverse proxy.
- Capture failure evidence from logs before changing config.
- Apply smallest fix first, then re-verify.

## Incident Triage

- Startup failure: inspect import/config/db connection first.
- 5xx from nginx: verify upstream container and route mapping.
- Auth failures: verify token env and clock consistency.
- Data failures: verify DB URL, migrations, credentials.

## References

- Read `references/checklists.md` for deploy and rollback checklists.

---
name: project-delivery-orchestrator
description: Orchestrate end-to-end task delivery for this project by sequencing planning, implementation, validation, cleanup, and deployment steps. Use when tasks span multiple concerns, require coordinated execution across modules, or need a clear done-definition with verification artifacts.
---

# Project Delivery Orchestrator

## Orchestration Flow

1. Translate request into concrete deliverables.
2. Split work into backend, standards, cleanup, and deploy tracks.
3. Sequence tracks to reduce integration risk.
4. Execute and validate each track.
5. Produce final change summary and verification status.

## Skill Routing

- Use `project-backend-dev` for feature implementation.
- Use `project-code-standards` for quality gate and risk scan.
- Use `project-code-cleanup` for refactor and structure hygiene.
- Use `project-deploy-ops` for deployment and runtime checks.

## Done Definition

- Code changes are complete and scoped to request.
- Tests or smoke checks are executed and reported.
- Known risks and follow-ups are explicitly listed.
- Deployment impact is documented when relevant.

## References

- Read `references/checklists.md` for sequencing templates.

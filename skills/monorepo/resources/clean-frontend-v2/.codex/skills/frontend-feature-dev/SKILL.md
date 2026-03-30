---
name: frontend-feature-dev
description: Implement frontend features in this repository using the established folder structure, health-check pattern, and TypeScript quality gates. Use when adding new pages/components/hooks/api modules, wiring feature flows, or expanding existing frontend functionality in clean-frontend-v2.
---

# Frontend Feature Dev

Implement features with predictable structure and minimal regressions.

## Execution Flow

1. Read `PROJECT_STRUCTURE.md` and map the request to target folders before coding.
2. Create files in the correct layers: `api` for requests, `models` for mapping, `hooks` for stateful orchestration, `pages/components` for UI.
3. Keep business logic outside UI components.
4. Run `npm run typecheck` and `npm run build` after edits.
5. Update docs when feature behavior or structure changes.

## Placement Rules

- Put endpoint calls in `src/api/<domain>/`.
- Put API response and shared types in `src/types/`.
- Put transformation logic in `src/models/`.
- Put reusable async/view logic in `src/hooks/`.
- Keep page components thin and composition-focused.

## Output Requirements

- Keep files small and cohesive.
- Avoid hidden coupling across domains.
- Add only necessary dependencies.
- Preserve compatibility with Docker runtime and `/health` endpoint.

## References

- Read `references/feature-checklist.md` before implementing large feature requests.

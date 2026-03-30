# Feature Checklist

## Before coding

- Confirm feature scope and acceptance criteria.
- Identify affected layers (`api`, `models`, `hooks`, `components/pages`).
- Reuse existing modules where possible.

## During coding

- Keep API calls in `src/api`.
- Keep transformation in `src/models`.
- Keep async/error/loading orchestration in `src/hooks`.
- Keep UI focused on rendering and interactions.

## Before handoff

- Run `npm run typecheck`.
- Run `npm run build`.
- Update docs if behavior or setup changed.

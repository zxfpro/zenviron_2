---
name: frontend-code-cleanup
description: Refactor and organize the frontend codebase to reduce clutter, remove dead code, and improve readability without changing intended behavior. Use when requests involve cleanup, restructuring folders, consolidating duplicated utilities, or preparing the project for long-term maintenance.
---

# Frontend Code Cleanup

Clean and reorganize code while preserving behavior.

## Cleanup Workflow

1. Inventory files and locate duplication or dead code.
2. Propose target structure using current project conventions.
3. Apply small, verifiable refactors per module.
4. Re-run typecheck and build after cleanup.
5. Summarize moved, removed, and consolidated parts.

## Cleanup Priorities

- Remove unused modules and exports.
- Deduplicate similar utilities and helpers.
- Normalize file naming and folder placement.
- Simplify overly large components by splitting concerns.

## Safety Rules

- Avoid behavior changes unless explicitly requested.
- Keep public module contracts stable or document changes.
- Prefer incremental edits over massive rewrites.

## References

- Follow `references/cleanup-playbook.md` for deterministic cleanup steps.

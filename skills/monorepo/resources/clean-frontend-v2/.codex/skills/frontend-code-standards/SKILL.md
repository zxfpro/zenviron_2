---
name: frontend-code-standards
description: Enforce code quality, architectural boundaries, and maintainable conventions for this frontend project. Use when reviewing pull requests, standardizing module layout, checking naming and typing quality, or preventing structural drift from the project conventions.
---

# Frontend Code Standards

Apply review-grade standards before merging or delivering code.

## Review Workflow

1. Validate placement against `PROJECT_STRUCTURE.md`.
2. Check TypeScript strictness and avoid `any` unless justified.
3. Verify separation of concerns across `api/models/hooks/ui`.
4. Confirm naming clarity for files, functions, and exported types.
5. Require build and type-check success.

## Hard Rules

- Do not place raw fetch logic in UI files.
- Do not mix mapping logic with request logic.
- Prefer explicit return types for exported functions.
- Keep module responsibilities narrow.
- Remove dead code and stale comments in touched files.

## References

- Use `references/review-checklist.md` for structured audits.

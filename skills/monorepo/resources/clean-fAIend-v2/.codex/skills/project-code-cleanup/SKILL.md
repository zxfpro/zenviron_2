---
name: project-code-cleanup
description: Refactor and organize code for readability, modularity, and long-term maintainability in this project. Use when removing dead code, splitting large files, deduplicating logic, normalizing naming, or restructuring modules without changing intended behavior.
---

# Project Code Cleanup

## Cleanup Workflow

1. Map current behavior and call graph.
2. Propose minimal-risk refactor slices.
3. Apply one slice at a time.
4. Run tests or smoke checks after each slice.
5. Stop if unexpected external changes appear.

## Cleanup Scope

- Remove unused imports, functions, and stale comments.
- Extract repeated logic to shared helpers.
- Split oversized modules by responsibility.
- Normalize naming and error messages.
- Keep public interfaces stable unless explicitly changed.

## Safety Rules

- Preserve runtime behavior by default.
- Make mechanical refactors separately from behavior changes.
- Add regression tests around touched critical flows.

## References

- Read `references/checklists.md` for safe refactor sequencing.

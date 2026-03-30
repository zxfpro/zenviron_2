---
name: project-code-standards
description: Enforce project coding standards, testing gates, and review quality for this repository. Use when reviewing pull-ready changes, validating architecture consistency, checking security-sensitive code paths, improving readability, or preparing code for release.
---

# Project Code Standards

## Quality Gate

1. Validate correctness before style.
2. Validate tests and regression coverage.
3. Validate security and configuration hygiene.
4. Validate maintainability and module boundaries.

## Review Priorities

- Identify behavior regressions first.
- Identify missing tests for changed logic.
- Identify insecure defaults, leaked secrets, weak auth checks.
- Identify hidden coupling and oversized functions.
- Identify naming and API contract ambiguity.

## Required Outputs

- List findings ordered by severity.
- Attach file path and line reference for each finding.
- State residual risks when no findings are detected.

## Standards

- Keep files focused and avoid multi-responsibility modules.
- Prefer immutable transforms and explicit return values.
- Avoid silent exception swallowing.
- Keep logs actionable and free of sensitive data.

## References

- Read `references/checklists.md` for release and review checklists.

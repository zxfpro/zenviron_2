---
name: module-factory
description: Scaffold and package reusable module skills from completed features.
version: 0.2.0
---

# module-factory

Skill Version: `0.2.0`

This is the public entry for module skill packaging. It creates `module-<slug>`
skills that support direct copy + integration micro-adjust.

## When to use

- You completed a feature module and want to reuse it in other projects.
- You need a low-barrier packaging flow with docs/tests/E2E gate checks.

## Instructions

1. Generate a module skill:
   - `bash "$SKILL_DIR/resources/scripts/new_module_skill.sh" auth-login`
2. Fill `resources/module/*` with feature payload.
3. Fill `resources/spec/*` with integration and verification docs.
4. Run gate check:
   - `bash "$SKILL_DIR/resources/scripts/validate_gate.sh" "<generated-module-skill-dir>"`
5. Import into target project:
   - `bash "$SKILL_DIR/resources/scripts/import_module.sh" "<generated-module-skill-dir>" "<target-project-dir>"`

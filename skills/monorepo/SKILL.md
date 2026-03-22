---
name: monorepo
description: Bootstrap an AI-ready monorepo project using Zenviron's monorepo template.
---

# monorepo

Use this skill to initialize a new AI-ready monorepo from `template/monorepo/skeleton`.

## When to use

- You want a clean project baseline with app/package/docs folders.
- You need placeholder rendering for project identity fields.
- You want a repeatable bootstrap command for new repositories.

## Instructions

1. Run `uv run zenviron init "<project_name>" --template monorepo`.
2. If needed, add `--target-dir <path>` to control output location.
3. Verify generated files include `.zenviron-state.json`.
4. Confirm placeholders are rendered:
   - `{{ PROJECT_NAME }}`
   - `{{ MODULE_NAME }}`
   - `{{ REPO_SLUG }}`

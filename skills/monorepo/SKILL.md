---
name: monorepo
description: Bootstrap an AI-ready monorepo project using Zenviron's monorepo template.
version: 0.2.4
---

# monorepo

Skill Version: `0.2.4`

Use this skill to initialize a new AI-ready monorepo from bundled local resources.

## When to use

- You want a clean project baseline with app/package/docs folders.
- You need placeholder rendering for project identity fields.
- You want a repeatable bootstrap command for new repositories.

## Instructions

1. Preflight confirmation (must ask user before generation):
   - Confirm target base directory is `~/GitHub` (default, unless user explicitly changes it).
   - Confirm repository name (example: `foodmenu`).
   - Confirm template mode:
     - `skeleton` (default monorepo scaffold)
     - `clean-backend` (backend-focused scaffold)
2. Preflight self-check must run through shell script:
   - `bash "$SKILL_DIR/resources/scripts/preflight_check.sh"`
3. If the script fails, stop and require the user to complete `gh` authentication before continuing.
4. Resolve this skill folder path (`$SKILL_DIR`) and use fixed target base:
   - Typical install path: `~/.agents/skills/monorepo`
   - `TARGET_DIR="$HOME/GitHub"`
   - `PROJECT_NAME="<project-name>"`
   - `MODE="<skeleton|clean-backend>"`
5. Create the project under `~/GitHub`:
   - `mkdir -p "$TARGET_DIR"`
   - `cp -R "$SKILL_DIR/resources/$MODE" "$TARGET_DIR/$PROJECT_NAME"`
6. Render placeholders in text files:
   - `PROJECT_NAME` => display name
   - `MODULE_NAME` => snake_case name
   - `REPO_SLUG` => kebab-case name
7. Ensure generated files include `.zenviron-state.json` (create it if your workflow expects Zenviron state tracking).
8. Confirm placeholders are fully rendered with no `{{ ... }}` left.

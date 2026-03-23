---
name: monorepo
description: Bootstrap an AI-ready monorepo project using Zenviron's monorepo template.
version: 0.2.2
---

# monorepo

Skill Version: `0.2.2`

Use this skill to initialize a new AI-ready monorepo from the bundled local resources in `resources/skeleton`.

## When to use

- You want a clean project baseline with app/package/docs folders.
- You need placeholder rendering for project identity fields.
- You want a repeatable bootstrap command for new repositories.

## Instructions

1. Preflight confirmation (must ask user before generation):
   - Confirm target base directory is `~/GitHub` (default, unless user explicitly changes it).
   - Confirm repository name (example: `foodmenu`).
   - Confirm GitHub auth readiness with `gh auth status`.
2. Preflight self-check commands (run automatically when possible):
   - `gh auth status`
3. If `gh auth status` fails, stop and require the user to complete `gh` authentication before continuing.
4. Resolve this skill folder path (`$SKILL_DIR`) and use fixed target base:
   - Typical install path: `~/.agents/skills/monorepo`
   - `TARGET_DIR="$HOME/GitHub"`
   - `PROJECT_NAME="<project-name>"`
5. Create the project under `~/GitHub`:
   - `mkdir -p "$TARGET_DIR"`
   - `cp -R "$SKILL_DIR/resources/skeleton" "$TARGET_DIR/$PROJECT_NAME"`
6. Render placeholders in text files:
   - `PROJECT_NAME` => display name
   - `MODULE_NAME` => snake_case name
   - `REPO_SLUG` => kebab-case name
7. Ensure generated files include `.zenviron-state.json` (create it if your workflow expects Zenviron state tracking).
8. Confirm placeholders are fully rendered with no `{{ ... }}` left.

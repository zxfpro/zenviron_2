---
name: monorepo
description: Bootstrap an AI-ready monorepo project using Zenviron's monorepo template.
---

# monorepo

Use this skill to initialize a new AI-ready monorepo from the bundled local resources in `resources/skeleton`.

## When to use

- You want a clean project baseline with app/package/docs folders.
- You need placeholder rendering for project identity fields.
- You want a repeatable bootstrap command for new repositories.

## Instructions

1. Resolve this skill folder path (`$SKILL_DIR`) and set output directory:
   - Typical install path: `~/.agents/skills/monorepo`
   - `TARGET_DIR="<your-target-parent-dir>"`
   - `PROJECT_NAME="<project-name>"`
2. Copy bundled template resources:
   - `cp -R "$SKILL_DIR/resources/skeleton" "$TARGET_DIR/$PROJECT_NAME"`
3. Render placeholders in text files:
   - `PROJECT_NAME` => display name
   - `MODULE_NAME` => snake_case name
   - `REPO_SLUG` => kebab-case name
4. Verify generated files include `.zenviron-state.json` (create it if your workflow expects Zenviron state tracking).
5. Confirm placeholders are fully rendered with no `{{ ... }}` left.

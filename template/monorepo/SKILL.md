# Monorepo Project Bootstrap Skill

Use this skill to create a new AI-ready monorepo project from `template/monorepo/skeleton`.

## Responsibilities
- Create project directory from template skeleton.
- Replace placeholders: `{{ PROJECT_NAME }}`, `{{ MODULE_NAME }}`, `{{ REPO_SLUG }}`.
- Ensure `.zenviron-state.json` is generated.
- Suggest repository candidates for GitHub name conflicts.

## Usage
- Prefer `zenviron init <project_name> --template monorepo`.
- For skills-only install, use `zenviron skills install --mode project`.
- For ecosystem install, use `npx skills add <your-org>/<your-repo>`.

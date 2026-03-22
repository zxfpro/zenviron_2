# Thread Handoff (zenviron_2)

## Goal
Convert Zenviron into a skills-first public GitHub repository for AI project bootstrap and distribution via skills.sh.

## What has been implemented
- New Python CLI (`zenviron`) with commands:
  - `templates list`
  - `init <project_name> --template <name>`
  - `skills install --mode project|user`
  - `doctor`
- New convention-based template system under `template/<name>/` (no central registry).
- Default templates:
  - `monorepo` (AI-ready project skeleton)
  - `sql-docker` (PostgreSQL via Docker Compose)
- Placeholder rendering supported:
  - `{{ PROJECT_NAME }}`
  - `{{ MODULE_NAME }}`
  - `{{ REPO_SLUG }}`
- Local name conflict handling:
  - `name`, `name-2`, `name-3`, ... then timestamp fallback.
- State file generated on init:
  - `.zenviron-state.json`
- README includes:
  - how to add template
  - how to update repo
  - skills.sh distribution notes

## Current status
- Repo path: `/Users/zxf/GitHub/zenviron_2`
- Remote: `https://github.com/zxfpro/zenviron_2.git`
- Visibility: public
- Tests currently pass in local verification (`pytest`).

## Recommended next steps
1. Commit and push current changes.
2. Validate public install:
   - `npx skills add zxfpro/zenviron_2`
   - `npx skills add https://github.com/zxfpro/zenviron_2 --skill monorepo`
   - `npx skills add https://github.com/zxfpro/zenviron_2 --skill sql-docker`
3. Publish Python CLI to PyPI (token already prepared).
4. Tag first public release (suggestion: `v0.2.0`).

## Quick commands
```bash
uv sync
uv run pytest -q
uv run zenviron templates list
uv run zenviron init "Demo Project" --template monorepo --target-dir /tmp
uv run zenviron init "SQL Demo" --template sql-docker --target-dir /tmp
```

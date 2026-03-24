# Zenviron

Zenviron is an AI-ready project bootstrap and skills distribution repository.

## What It Provides

- Convention-based template discovery under `template/<name>/`
- `monorepo` template for full AI-ready project bootstrap
- `sql-docker` template for fast local PostgreSQL runtime
- Python CLI for init, templates listing, skills install, and doctor checks
- Skills.sh-first distribution workflow

## Install

```bash
uv sync
uv run zenviron --help
```

Or install as a tool:

```bash
uv tool install .
```

## Commands

```bash
zenviron templates list
zenviron init "My Project" --template monorepo
zenviron init "My DB Stack" --template sql-docker
zenviron skills install --mode project --dest ./.agents/skills/monorepo
zenviron doctor
```

## Skills.sh Distribution

Recommended:

```bash
npx skills add <your-org>/<your-repo>
```

Optional per skill:

```bash
npx skills add <repo-url> --skill monorepo
npx skills add <repo-url> --skill sql-docker
```

Published skills are defined under:

```text
skills/<skill-name>/SKILL.md
```

`SKILL.md` must include YAML frontmatter with `name` and `description`.
If a skill needs local static assets after installation, include them under:

```text
skills/<skill-name>/resources/
```

## Template Contract

Every template lives in a single folder:

```text
template/<template_name>/
├── skeleton/
├── SKILL.md
├── hooks/                # optional
└── variables.example.toml # optional
```

To add a new template, copy `template/monorepo` and rename the folder. No central config needed.

## How To Add A New Template

Use this workflow when adding a brand-new template (for both humans and agents):

1. Copy an existing template folder:

```bash
cp -R template/monorepo template/<new-template-name>
```

2. Update the copied template content:
- Edit `template/<new-template-name>/skeleton/**`
- Edit `template/<new-template-name>/SKILL.md`
- Optionally add:
  - `template/<new-template-name>/hooks/pre_create.sh`
  - `template/<new-template-name>/hooks/post_create.sh`
  - `template/<new-template-name>/variables.example.toml`

3. Keep placeholder support in text files:
- `{{ PROJECT_NAME }}`
- `{{ MODULE_NAME }}`
- `{{ REPO_SLUG }}`

4. Verify auto-discovery:

```bash
uv run zenviron templates list
```

5. Verify template initialization:

```bash
uv run zenviron init "Template Smoke Test" --template <new-template-name> --target-dir /tmp
```

No central registry update is required. Folder-based convention is the source of truth.

## How To Update This Repository

Use this workflow when maintaining or evolving Zenviron:

1. Modify template(s) under `template/<name>/`.
2. If CLI behavior changes, update:
- `src/zenviron/cli.py`
- `src/zenviron/templating.py`
- `tests/test_cli.py`
3. Run verification:

```bash
uv sync
uv run pytest -q
uv run zenviron templates list
```

4. Update docs (`README.md`) if command behavior or template contract changed.
5. Bump version in `pyproject.toml` when shipping user-visible changes.

## Skills.sh Publishing Notes

Recommended distribution path:

```bash
npx skills add <your-org>/<your-repo>
```

Per-skill installation:

```bash
npx skills add <repo-url> --skill <template-name>
```

As long as `skills/<name>/SKILL.md` exists (with valid frontmatter) and the repo is accessible, skills can be discovered and installed.

## Skill Versioning

Each published skill includes:

- `skills/<name>/SKILL.md` frontmatter field: `version`
- `skills/<name>/VERSION.md` markdown version file

After installing, verify local installed version:

```bash
cat ~/.agents/skills/monorepo/VERSION.md
cat ~/.agents/skills/sql-docker/VERSION.md
```

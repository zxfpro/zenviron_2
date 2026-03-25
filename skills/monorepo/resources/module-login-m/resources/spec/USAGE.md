# Usage

## Quick Start

1. Import to target project:
   - `bash resources/scripts/import_module.sh <module-skill-dir> <target-project-dir>`
2. Install backend deps from imported `pyproject.toml`.
3. Configure env (`JWT_SECRET`, `DATABASE_URL`, SMTP keys).
4. Start backend and frontend static hosting.
5. Run tests.

## Verification

- Test command:
  - `uv run pytest`
- E2E command:
  - `curl /auth/register/email/code` -> `curl /auth/register_with_code` -> `curl /auth/login`

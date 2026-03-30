# Standards Checklists

## PR Review

- Behavior change is intentional and documented.
- New branches and edge cases are tested.
- Error handling is explicit.
- Configuration is environment-driven.
- No debug artifacts or dead code remain.

## Release Gate

- Tests pass in local or CI target environment.
- Required env vars are documented.
- Logging level and verbosity are production-safe.
- Migration and rollback path is clear.

# Cleanup Playbook

## Detect

- Find dead files and stale exports.
- Find duplicated logic patterns.
- Find mixed-responsibility modules.

## Refactor

- Extract shared logic into `utils`, `hooks`, or `services`.
- Move misplaced files to correct directories.
- Split oversized files into cohesive units.

## Verify

- Build and typecheck pass.
- Imports resolve cleanly.
- No orphaned references remain.

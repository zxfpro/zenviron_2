# Deploy Ops Checklists

## Pre-Deploy

- Required `.env` keys are set.
- Compose file targets expected image and ports.
- Database and persistent volumes are reachable.

## Post-Deploy

- Containers are healthy.
- `/` and critical API endpoints respond.
- nginx proxy path rewrites behave as expected.
- Logs show no repeated crash loops.

## Rollback

- Previous known-good image tag is known.
- Command to restart with previous image is prepared.
- Validation checks are rerun after rollback.

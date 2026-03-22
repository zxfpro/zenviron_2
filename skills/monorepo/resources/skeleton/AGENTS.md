# {{ PROJECT_NAME }} Agent Rules

## Goal
Deliver features with safe, test-first, small-batch changes.

## Required Workflow
1. Clarify scope and acceptance criteria.
2. Implement in small commits.
3. Run relevant tests before completion.
4. Document risks and rollback notes.

## Safety
- Never expose secrets in logs or commits.
- Avoid destructive git operations.

## Testing Baseline
- Unit tests for core behavior.
- Integration tests for critical flows.

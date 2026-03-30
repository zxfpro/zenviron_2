# Backend Delivery Checklists

## New API Endpoint

- Define schema classes for request and response.
- Validate auth requirement and required scopes.
- Implement service layer and keep side effects isolated.
- Add route and include router registration.
- Add tests for success path and one failure path.

## Runtime Stability

- Confirm imports resolve at app startup.
- Confirm env defaults do not expose secrets.
- Confirm DB session lifecycle is explicit.
- Confirm errors are logged with useful context.

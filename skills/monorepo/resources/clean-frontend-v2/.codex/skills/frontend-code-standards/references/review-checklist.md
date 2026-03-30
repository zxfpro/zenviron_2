# Review Checklist

## Architecture

- Is each file in the correct folder?
- Is API access isolated from UI?
- Are shared types centralized appropriately?

## Type quality

- Are exported APIs strongly typed?
- Is `any` avoided or justified?
- Are null/undefined cases handled?

## Maintainability

- Is function scope clear and concise?
- Are names specific and stable?
- Is unused code removed?

## Verification

- `npm run typecheck`
- `npm run build`

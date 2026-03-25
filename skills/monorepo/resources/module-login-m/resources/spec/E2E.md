# E2E Core Flow

core flow: user registers by email code, logs in, fetches `/auth/me`, and optionally logs in by phone code.

status: passed

## Steps

1. Send register code and complete email registration.
2. Login with email/password and verify token-based `/auth/me`.
3. Send phone code and login by phone code.
4. Verify frontend has email/phone login entry and route works.

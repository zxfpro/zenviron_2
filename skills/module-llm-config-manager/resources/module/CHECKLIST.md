# Integration Checklist

- [ ] Backend service starts and `/health` returns 200
- [ ] Frontend page opens and loads profiles
- [ ] Save profile writes into TOML
- [ ] Active alias switching works
- [ ] Delete profile works (except last profile)
- [ ] Alias rename behaves as rename (no stale old alias)
- [ ] SSE file-to-page sync works
- [ ] `uv run pytest -q` passes
- [ ] `npm run build` passes

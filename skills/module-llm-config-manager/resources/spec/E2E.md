# E2E

- core flow: load profiles -> edit/save -> switch active alias -> delete profile -> external file edit sync
- status: passed

## Steps

1. Open `/hub`, confirm profile dropdown populated.
2. Modify a profile and save; verify TOML changed.
3. Open `/keys`, switch active alias; verify `meta.active_alias` changed.
4. Delete a non-last profile; verify removed in UI and TOML.
5. Edit TOML externally; verify page reflects change.

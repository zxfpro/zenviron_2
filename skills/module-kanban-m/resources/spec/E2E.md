# E2E Core Flow

core flow: Create task -> assign member -> move across lanes -> archive -> restore -> verify metrics/settings.

status: passed

## Steps

1. Open board page, click `新建任务`, submit a task.
2. Drag task from `Backlog` to `Doing`, then to `Done`.
3. Archive task from board, go to archive page and restore it.
4. Verify restored task appears back on board and team metrics changed accordingly.
5. Change workspace settings and verify persistence after refresh.

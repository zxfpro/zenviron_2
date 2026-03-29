import os

from contextlib import contextmanager

from fastapi.testclient import TestClient

os.environ['KANBAN_DATABASE_URL'] = 'sqlite://'

from kanban_api.main import create_app  # noqa: E402


@contextmanager
def get_client():
  app = create_app('sqlite://')
  with TestClient(app) as client:
    yield client


def test_board_bootstrap() -> None:
  with get_client() as client:
    response = client.get('/board')
    assert response.status_code == 200
    payload = response.json()
    assert payload['workspace_name'] == 'Project Alpha'
    assert len(payload['columns']) >= 5
    assert len(payload['members']) >= 4


def test_task_crud_move_archive_restore() -> None:
  with get_client() as client:
    board = client.get('/board').json()
    columns = board['columns']
    members = board['members']

    create_res = client.post(
      '/tasks',
      json={
        'title': 'Test task',
        'description': 'Created in test',
        'priority': 'high',
        'column_id': columns[0]['id'],
        'assignee_id': members[0]['id'],
      },
    )
    assert create_res.status_code == 200
    task = create_res.json()
    task_id = task['id']

    patch_res = client.patch(f'/tasks/{task_id}', json={'title': 'Test task updated'})
    assert patch_res.status_code == 200
    assert patch_res.json()['title'] == 'Test task updated'

    move_res = client.patch(f'/tasks/{task_id}/move', json={'column_id': columns[1]['id']})
    assert move_res.status_code == 200
    assert move_res.json()['column_id'] == columns[1]['id']

    archive_res = client.post(f'/tasks/{task_id}/archive')
    assert archive_res.status_code == 200
    assert archive_res.json()['archived'] is True

    restore_res = client.post(f'/tasks/{task_id}/restore')
    assert restore_res.status_code == 200
    assert restore_res.json()['archived'] is False

    delete_res = client.delete(f'/tasks/{task_id}')
    assert delete_res.status_code == 200
    assert delete_res.json()['ok'] is True


def test_metrics_and_settings() -> None:
  with get_client() as client:
    metrics = client.get('/team/metrics')
    assert metrics.status_code == 200
    assert 'workload' in metrics.json()
    assert 'member_metrics' in metrics.json()

    settings = client.get('/workspace/settings')
    assert settings.status_code == 200
    assert settings.json()['theme'] in ['light', 'dark']

    patched = client.patch('/workspace/settings', json={'workspace_name': 'Workspace Z', 'theme': 'dark'})
    assert patched.status_code == 200
    assert patched.json()['workspace_name'] == 'Workspace Z'
    assert patched.json()['theme'] == 'dark'

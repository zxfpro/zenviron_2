from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, col, func, select

from .database import get_session
from .models import ActivityAction, Column, Member, Priority, Task, TaskActivity, Workspace, WorkspaceSetting
from .schemas import (
    ActivityRead,
    BoardColumn,
    BoardResponse,
    MemberMetrics,
    MemberRead,
    TaskCreate,
    TaskMove,
    TaskPatch,
    TaskRead,
    TeamMetricsResponse,
    WorkspaceSettingPatch,
    WorkspaceSettingRead,
)

router = APIRouter()


def _task_code(session: Session) -> str:
    codes = session.exec(select(Task.code)).all()
    max_num = 100
    for raw in codes:
        code = raw
        if isinstance(raw, (tuple, list)):
            code = raw[0] if raw else None
        if code is None:
            continue
        try:
            num = int(str(code).split('-')[-1])
        except ValueError:
            continue
        if num > max_num:
            max_num = num
    return f'KAN-{max_num + 1}'


def _add_activity(session: Session, task_id: int, action: ActivityAction, details: str) -> None:
    session.add(TaskActivity(task_id=task_id, action=action, details=details))


@router.get('/members', response_model=list[MemberRead])
def get_members(session: Session = Depends(get_session)):
    return session.exec(select(Member).order_by(Member.id)).all()


@router.get('/tasks', response_model=list[TaskRead])
def get_tasks(
    archived: bool | None = None,
    q: str | None = None,
    priority: Priority | None = None,
    assignee_id: int | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(Task)
    if archived is not None:
        stmt = stmt.where(Task.archived == archived)
    if q:
        like_term = f'%{q}%'
        stmt = stmt.where((col(Task.title).like(like_term)) | (col(Task.description).like(like_term)))
    if priority:
        stmt = stmt.where(Task.priority == priority)
    if assignee_id:
        stmt = stmt.where(Task.assignee_id == assignee_id)

    return session.exec(stmt.order_by(Task.updated_at.desc())).all()


@router.post('/tasks', response_model=TaskRead)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    column = session.get(Column, payload.column_id)
    if not column:
        raise HTTPException(status_code=404, detail='Column not found')

    if payload.assignee_id:
        member = session.get(Member, payload.assignee_id)
        if not member:
            raise HTTPException(status_code=404, detail='Assignee not found')

    task = Task(
        code=_task_code(session),
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        due_date=payload.due_date,
        workspace_id=1,
        column_id=payload.column_id,
        assignee_id=payload.assignee_id,
    )
    session.add(task)
    session.flush()
    _add_activity(session, task.id, ActivityAction.CREATED, f'Task {task.code} created')
    session.commit()
    session.refresh(task)
    return task


@router.patch('/tasks/{task_id}', response_model=TaskRead)
def patch_task(task_id: int, payload: TaskPatch, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    data = payload.model_dump(exclude_unset=True)
    if 'assignee_id' in data and data['assignee_id']:
        member = session.get(Member, data['assignee_id'])
        if not member:
            raise HTTPException(status_code=404, detail='Assignee not found')

    for key, value in data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    _add_activity(session, task.id, ActivityAction.UPDATED, f'Task {task.code} updated')
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete('/tasks/{task_id}')
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    session.delete(task)
    session.commit()
    return {'ok': True}


@router.patch('/tasks/{task_id}/move', response_model=TaskRead)
def move_task(task_id: int, payload: TaskMove, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')

    column = session.get(Column, payload.column_id)
    if not column:
        raise HTTPException(status_code=404, detail='Column not found')

    task.column_id = payload.column_id
    task.updated_at = datetime.utcnow()
    _add_activity(session, task.id, ActivityAction.MOVED, f'Task {task.code} moved to {column.name}')
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post('/tasks/{task_id}/archive', response_model=TaskRead)
def archive_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    if task.archived:
        raise HTTPException(status_code=409, detail='Task already archived')

    task.archived = True
    task.updated_at = datetime.utcnow()
    _add_activity(session, task.id, ActivityAction.ARCHIVED, f'Task {task.code} archived')
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.post('/tasks/{task_id}/restore', response_model=TaskRead)
def restore_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    if not task.archived:
        raise HTTPException(status_code=409, detail='Task is not archived')

    task.archived = False
    task.updated_at = datetime.utcnow()
    _add_activity(session, task.id, ActivityAction.RESTORED, f'Task {task.code} restored')
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get('/board', response_model=BoardResponse)
def get_board(session: Session = Depends(get_session)):
    workspace = session.get(Workspace, 1)
    if not workspace:
        raise HTTPException(status_code=404, detail='Workspace not found')

    columns = session.exec(select(Column).where(Column.workspace_id == 1).order_by(Column.order)).all()
    tasks = session.exec(select(Task).where(Task.archived == False).order_by(Task.updated_at.asc())).all()  # noqa: E712
    members = session.exec(select(Member).order_by(Member.id)).all()

    grouped: dict[int, list[TaskRead]] = {}
    for task in tasks:
        grouped.setdefault(task.column_id, []).append(TaskRead.model_validate(task))

    response_columns = [
        BoardColumn(id=col_.id, name=col_.name, order=col_.order, tasks=grouped.get(col_.id, [])) for col_ in columns
    ]

    return BoardResponse(
        workspace_name=workspace.name,
        columns=response_columns,
        members=[MemberRead.model_validate(m) for m in members],
    )


@router.get('/team/metrics', response_model=TeamMetricsResponse)
def get_team_metrics(session: Session = Depends(get_session)):
    columns = session.exec(select(Column)).all()
    col_map = {c.id: c.name for c in columns}
    tasks = session.exec(select(Task).where(Task.archived == False)).all()  # noqa: E712
    members = session.exec(select(Member).order_by(Member.id)).all()
    activities = session.exec(select(TaskActivity).order_by(TaskActivity.created_at.desc()).limit(10)).all()

    workload: dict[str, int] = {}
    for task in tasks:
        c_name = col_map.get(task.column_id, 'Unknown')
        workload[c_name] = workload.get(c_name, 0) + 1

    metrics: list[MemberMetrics] = []
    for member in members:
        member_tasks = [t for t in tasks if t.assignee_id == member.id]
        doing_tasks = sum(1 for t in member_tasks if col_map.get(t.column_id) == 'Doing')
        done_tasks = sum(1 for t in member_tasks if col_map.get(t.column_id) == 'Done')
        metrics.append(
            MemberMetrics(
                member=MemberRead.model_validate(member),
                total_tasks=len(member_tasks),
                doing_tasks=doing_tasks,
                done_tasks=done_tasks,
            )
        )

    return TeamMetricsResponse(
        workload=workload,
        member_metrics=metrics,
        recent_activity=[ActivityRead.model_validate(a) for a in activities],
    )


@router.get('/workspace/settings', response_model=WorkspaceSettingRead)
def get_workspace_settings(session: Session = Depends(get_session)):
    workspace = session.get(Workspace, 1)
    setting = session.exec(select(WorkspaceSetting).where(WorkspaceSetting.workspace_id == 1)).first()
    if not workspace or not setting:
        raise HTTPException(status_code=404, detail='Workspace settings not found')
    return WorkspaceSettingRead(workspace_name=workspace.name, theme=setting.theme)


@router.patch('/workspace/settings', response_model=WorkspaceSettingRead)
def patch_workspace_settings(payload: WorkspaceSettingPatch, session: Session = Depends(get_session)):
    workspace = session.get(Workspace, 1)
    setting = session.exec(select(WorkspaceSetting).where(WorkspaceSetting.workspace_id == 1)).first()
    if not workspace or not setting:
        raise HTTPException(status_code=404, detail='Workspace settings not found')

    if payload.workspace_name is not None:
        workspace.name = payload.workspace_name
        session.add(workspace)
    if payload.theme is not None:
        setting.theme = payload.theme
        session.add(setting)

    session.commit()
    session.refresh(workspace)
    session.refresh(setting)
    return WorkspaceSettingRead(workspace_name=workspace.name, theme=setting.theme)

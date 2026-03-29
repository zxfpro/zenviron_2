from __future__ import annotations

from sqlmodel import Session, select

from .models import Column, Member, Priority, Role, Task, Workspace, WorkspaceSetting


DEFAULT_MEMBERS = [
    {'name': 'Alex Rivers', 'email': 'alex@kanban.local', 'role': Role.ADMIN},
    {'name': 'Mina Chen', 'email': 'mina@kanban.local', 'role': Role.PRODUCT},
    {'name': 'James Wilson', 'email': 'james@kanban.local', 'role': Role.DEVELOPER},
    {'name': 'Marco Rossi', 'email': 'marco@kanban.local', 'role': Role.TESTER},
]

DEFAULT_COLUMNS = ['Backlog', 'Ready', 'Waiting', 'Doing', 'Blocked', 'Done']



def seed_if_needed(session: Session) -> None:
    workspace = session.exec(select(Workspace).where(Workspace.id == 1)).first()
    if workspace:
        existing_columns = session.exec(
            select(Column).where(Column.workspace_id == workspace.id).order_by(Column.order)
        ).all()
        existing_names = {c.name for c in existing_columns}
        next_order = len(existing_columns)
        for name in DEFAULT_COLUMNS:
            if name not in existing_names:
                session.add(Column(workspace_id=workspace.id, name=name, order=next_order))
                next_order += 1
        session.commit()
        return

    workspace = Workspace(id=1, name='Project Alpha')
    session.add(workspace)
    session.add(WorkspaceSetting(workspace_id=1, theme='light'))

    members: list[Member] = []
    for m in DEFAULT_MEMBERS:
        member = Member(name=m['name'], email=m['email'], role=m['role'])
        session.add(member)
        members.append(member)

    session.flush()

    columns: list[Column] = []
    for idx, name in enumerate(DEFAULT_COLUMNS):
        col = Column(workspace_id=1, name=name, order=idx)
        session.add(col)
        columns.append(col)

    session.flush()

    demo_tasks = [
        Task(
            code='KAN-101',
            title='Implement task move API',
            description='Support moving task across board columns',
            priority=Priority.HIGH,
            workspace_id=1,
            column_id=columns[2].id,
            assignee_id=members[2].id,
        ),
        Task(
            code='KAN-102',
            title='Design archive table interactions',
            description='Build restore and inspect actions',
            priority=Priority.NORMAL,
            workspace_id=1,
            column_id=columns[1].id,
            assignee_id=members[1].id,
        ),
    ]
    for task in demo_tasks:
        session.add(task)

    session.commit()

from __future__ import annotations

from datetime import datetime, date
from enum import StrEnum
from typing import Optional

from sqlmodel import SQLModel, Field


class Role(StrEnum):
    ADMIN = 'admin'
    PRODUCT = 'product'
    DEVELOPER = 'developer'
    TESTER = 'tester'


class Priority(StrEnum):
    LOW = 'low'
    NORMAL = 'normal'
    HIGH = 'high'
    URGENT = 'urgent'


class ActivityAction(StrEnum):
    CREATED = 'created'
    UPDATED = 'updated'
    MOVED = 'moved'
    ARCHIVED = 'archived'
    RESTORED = 'restored'


class Workspace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(default='Project Alpha', max_length=100)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkspaceSetting(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(index=True, unique=True)
    theme: str = Field(default='light', max_length=20)


class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=80)
    email: str = Field(index=True, unique=True, max_length=120)
    role: Role
    avatar: str = Field(default='')
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Column(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    workspace_id: int = Field(index=True)
    name: str = Field(max_length=50)
    order: int = Field(index=True)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True, max_length=20)
    title: str = Field(max_length=200)
    description: str = Field(default='', max_length=1000)
    priority: Priority = Field(default=Priority.NORMAL)
    due_date: Optional[date] = Field(default=None)
    archived: bool = Field(default=False, index=True)
    workspace_id: int = Field(index=True)
    column_id: int = Field(index=True)
    assignee_id: Optional[int] = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskActivity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(index=True)
    action: ActivityAction
    details: str = Field(default='', max_length=400)
    actor_name: str = Field(default='system', max_length=80)
    created_at: datetime = Field(default_factory=datetime.utcnow)

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict

from .models import ActivityAction, Priority, Role


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: Role
    avatar: str
    active: bool


class ColumnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    order: int


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=1000)
    priority: Priority = Priority.NORMAL
    due_date: Optional[date] = None
    column_id: int
    assignee_id: Optional[int] = None


class TaskPatch(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    assignee_id: Optional[int] = None


class TaskMove(BaseModel):
    column_id: int


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    code: str
    title: str
    description: str
    priority: Priority
    due_date: Optional[date]
    archived: bool
    column_id: int
    assignee_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class BoardColumn(BaseModel):
    id: int
    name: str
    order: int
    tasks: list[TaskRead]


class BoardResponse(BaseModel):
    workspace_name: str
    columns: list[BoardColumn]
    members: list[MemberRead]


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    task_id: int
    action: ActivityAction
    details: str
    actor_name: str
    created_at: datetime


class MemberMetrics(BaseModel):
    member: MemberRead
    total_tasks: int
    doing_tasks: int
    done_tasks: int


class TeamMetricsResponse(BaseModel):
    workload: dict[str, int]
    member_metrics: list[MemberMetrics]
    recent_activity: list[ActivityRead]


class WorkspaceSettingRead(BaseModel):
    workspace_name: str
    theme: str


class WorkspaceSettingPatch(BaseModel):
    workspace_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    theme: Optional[str] = Field(default=None, pattern='^(light|dark)$')

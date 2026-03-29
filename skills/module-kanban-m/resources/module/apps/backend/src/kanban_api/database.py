from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

_engine = None


def init_engine(database_url: str):
    global _engine
    if database_url.startswith('sqlite'):
        connect_args = {'check_same_thread': False}
        kwargs = {'poolclass': StaticPool} if database_url == 'sqlite://' else {}
        _engine = create_engine(database_url, echo=False, connect_args=connect_args, **kwargs)
    else:
        _engine = create_engine(database_url, echo=False)
    return _engine


def get_engine():
    if _engine is None:
        raise RuntimeError('Engine is not initialized')
    return _engine


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(get_engine())


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session

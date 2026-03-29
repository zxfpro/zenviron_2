# AI_Amend 2026-01-24 数据库初始化
import os
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/test.db")
DB_ECHO = os.getenv("DB_ECHO", "false").lower() in {"1", "true", "yes"}
engine = create_engine(DATABASE_URL, echo=DB_ECHO)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from .api import router
from .config import settings
from .database import create_db_and_tables, get_engine, init_engine
from .seed import seed_if_needed


def create_app(database_url: str | None = None) -> FastAPI:
    init_engine(database_url or settings.database_url)

    app = FastAPI(title=settings.app_name)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    app.include_router(router)

    @app.on_event('startup')
    def on_startup() -> None:
        create_db_and_tables()
        with Session(get_engine()) as session:
            seed_if_needed(session)

    return app


app = create_app()

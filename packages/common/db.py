from contextlib import asynccontextmanager

import duckdb
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import get_settings


def _async_url(url: str) -> str:
    return url.replace("postgresql://", "postgresql+asyncpg://", 1)


def get_engine():
    return create_async_engine(_async_url(get_settings().database_url), pool_pre_ping=True)


@asynccontextmanager
async def get_session():
    maker = async_sessionmaker(get_engine(), expire_on_commit=False)
    async with maker() as session:
        yield session


def get_duckdb_conn(path: str = "data/research.duckdb"):
    return duckdb.connect(path)

from alembic import context
from packages.common.config import get_settings
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    get_settings().database_url.replace("postgresql://", "postgresql+asyncpg://", 1),
)
target_metadata = None


def run_migrations_offline():
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
    )
    context.run_migrations()


async def run_migrations_online():
    engine = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with engine.connect() as conn:
        await conn.run_sync(
            lambda c: (
                context.configure(connection=c, target_metadata=target_metadata)
                or context.run_migrations()
            )
        )
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())

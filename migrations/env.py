import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# Import models package to ensure all SQLModel tables are registered
from fastapi_tdd_docker.models import SQLModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# Importing the models package ensures all SQLModel tables are registered
target_metadata = SQLModel.metadata


def get_url() -> str:
    """
    Get database URL from environment or alembic.ini.
    Priority: APP_DATABASE_URL > DATABASE_URL > alembic.ini
    """
    url = os.getenv("APP_DATABASE_URL") or os.getenv("DATABASE_URL")
    if url:
        return url
    # Fallback to alembic.ini
    return config.get_main_option("sqlalchemy.url", "")


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# ---------- OFFLINE MODE ----------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    Run migrations without a DB connection.
    Generates SQL scripts using the URL from env or alembic.ini.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()


# def do_run_migrations(connection: Connection) -> None:
#     context.configure(connection=connection, target_metadata=target_metadata)

#     with context.begin_transaction():
#         context.run_migrations()


# async def run_async_migrations() -> None:
#     """In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """

#     connectable = async_engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix='sqlalchemy.',
#         poolclass=pool.NullPool,
#     )

#     async with connectable.connect() as connection:
#         await connection.run_sync(do_run_migrations)

#     await connectable.dispose()


# auto generated inital code
# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode."""

#     asyncio.run(run_async_migrations())


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


# ---------- ONLINE MODE ----------
def _run_migrations(connection: Connection) -> None:
    """
    Synchronous migration runner invoked inside an async connection.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=False,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Run migrations with a real DB connection.
    Creates its own AsyncEngine from environment variables or alembic.ini.
    This decouples Alembic from the app's engine lifecycle.
    """
    url = get_url()
    engine = create_async_engine(url, echo=False)

    async with engine.connect() as conn:
        await conn.run_sync(_run_migrations)

    await engine.dispose()


# ---------- ENTRY POINT ----------
def run() -> None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        import asyncio

        asyncio.run(run_migrations_online())


run()

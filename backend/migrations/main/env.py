import os
import sys
from logging.config import fileConfig
from decouple import config as decouple_config

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import models for autogenerate support
from app.db.base import Base
from app.models import *  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


# Override sqlalchemy.url with environment variables
section = config.config_ini_section
config.set_section_option(
    section, "ALEMBIC_MAIN_DB", decouple_config("ALEMBIC_MAIN_DB")
)
config.set_section_option(
    section, "ALEMBIC_TEST_DB", decouple_config("ALEMBIC_TEST_DB")
)


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
print("🔍 Alembic is connecting to: MAIN DB")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

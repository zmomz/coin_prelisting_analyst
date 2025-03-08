import os
from logging.config import fileConfig

from sqlalchemy import create_engine, pool
from alembic import context

# Import the Base model to detect migrations
from app.db.base import Base

# Alembic Configuration
config = context.config

# Logging Configuration
if config.config_file_name:
    fileConfig(config.config_file_name)

# Ensure the database URL is available
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Check your .env file!")

# Convert asyncpg to psycopg2 for Alembic migrations
SYNC_DATABASE_URL = DATABASE_URL.replace("asyncpg", "psycopg2")  # ✅ Convert async → sync

# Set Alembic to use the synchronous database URL
config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)

# Metadata for autogeneration
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=SYNC_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(SYNC_DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

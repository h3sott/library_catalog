from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from src.library_catalog.core.config import settings
from src.library_catalog.core.database import Base
from src.library_catalog.data.models import book  # noqa: F401

# Alembic Config object
config = context.config

# Настроим URL для Alembic: убираем +asyncpg
config.set_main_option(
    "sqlalchemy.url",
    str(settings.database_url).replace("+asyncpg", "")
)

# Настройка логирования
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# metadata всех моделей
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Создаем синхронный движок для Alembic
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()

# Запуск миграций
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
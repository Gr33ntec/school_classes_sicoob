import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import app.models  # noqa: F401
from app.core.config import database_url
from app.core.database import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
# Permite apontar migrations para outro schema (ex.: testes) via ALEMBIC_DB_NAME.
url = database_url(os.environ.get("ALEMBIC_DB_NAME"))


def run_migrations_online() -> None:
    engine = create_engine(url)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()

import asyncio
import os
from pathlib import Path

from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


# Load environment variables from .env or .env.example
env_file = '.env' if Path('.env').exists() else '.env.example'
load_dotenv(env_file)

BASE_TEST_DB = os.getenv('POSTGRES_DB', 'shopping_test_db')
WORKER_ID = os.getenv('PYTEST_XDIST_WORKER')
TEST_DB_NAME = f'{BASE_TEST_DB}_{WORKER_ID}' if WORKER_ID else BASE_TEST_DB
os.environ['POSTGRES_DB'] = TEST_DB_NAME

from src.main import app  # noqa: F403, E402
from tests.order.functional.fixtures import *  # noqa: F403, E402, E402
from tests.order.functional.given import *  # noqa: F403, E402
from tests.order.functional.then import *  # noqa: F403, E402
from tests.order.functional.when import *  # noqa: F403, E402
from tests.product.functional.fixtures import *  # noqa: F403, E402
from tests.product.functional.given import *  # noqa: F403, E402
from tests.product.functional.then import *  # noqa: F403, E402
from tests.product.functional.when import *  # noqa: F403, E402
from tests.pytest_bdd_ng_example.fixtures import *  # noqa: F403, E402
from tests.pytest_bdd_ng_example.given import *  # noqa: F403, E402
from tests.pytest_bdd_ng_example.then import *  # noqa: F403, E402
from tests.pytest_bdd_ng_example.when import *  # noqa: F403, E402
from tests.shared.given import *  # noqa: F403, E402
from tests.shared.then import *  # noqa: F403, E402
from tests.user.functional.fixtures import *  # noqa: F403, E402
from tests.user.functional.then import *  # noqa: F403, E402
from tests.user.functional.when import *  # noqa: F403, E402


DB_CONFIG = {
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_SERVER'),
    'port': os.getenv('POSTGRES_PORT'),
    'test_db': TEST_DB_NAME,
}
TEST_DATABASE_URL = f'postgresql+asyncpg://{DB_CONFIG["user"]}:{DB_CONFIG["password"]}@{DB_CONFIG["host"]}:{DB_CONFIG["port"]}/{DB_CONFIG["test_db"]}'


@pytest.fixture
def execute_sql_statement():
    def _execute(statement: str, params: dict | None = None, fetch: bool = False):
        async def _run():
            engine = create_async_engine(TEST_DATABASE_URL)
            async with engine.begin() as conn:
                result = await conn.execute(text(statement), params or {})
                if fetch:
                    return [dict(row._mapping) for row in result]
            await engine.dispose()
            return None

        return asyncio.run(_run())

    return _execute


async def execute_sql(url: str, statements: list, **engine_kwargs):
    engine = create_async_engine(url, **engine_kwargs)
    async with engine.begin() as conn:
        for stmt in statements:
            await conn.execute(text(stmt))
    await engine.dispose()


async def setup_test_database():
    postgres_url = TEST_DATABASE_URL.replace(f'/{DB_CONFIG["test_db"]}', '/postgres')
    engine = create_async_engine(postgres_url, isolation_level='AUTOCOMMIT')
    async with engine.begin() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_CONFIG['test_db']}'")
        )
        if not result.fetchone():
            await conn.execute(text(f'CREATE DATABASE {DB_CONFIG["test_db"]}'))
    await engine.dispose()
    await execute_sql(TEST_DATABASE_URL, ['DROP SCHEMA public CASCADE', 'CREATE SCHEMA public'])
    alembic_cfg = Config(Path(__file__).parent.parent / 'src/platform/alembic/alembic.ini')
    alembic_cfg.set_main_option('sqlalchemy.url', TEST_DATABASE_URL.replace('+asyncpg', ''))
    command.upgrade(alembic_cfg, 'head')


_cached_tables = None


async def clean_all_tables():
    global _cached_tables
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        if _cached_tables is None:
            result = await conn.execute(
                text(
                    "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename != 'alembic_version'"
                )
            )
            _cached_tables = [row[0] for row in result]
        if _cached_tables:
            quoted_tables = [f'"{table}"' for table in _cached_tables]
            await conn.execute(
                text(f'TRUNCATE {", ".join(quoted_tables)} RESTART IDENTITY CASCADE')
            )
    await engine.dispose()


def pytest_sessionstart(session):
    asyncio.run(setup_test_database())


@pytest.fixture(autouse=True)
async def clean_database():
    await clean_all_tables()
    yield


@pytest.fixture(scope='session')
def client():
    with TestClient(app) as test_client:
        yield test_client

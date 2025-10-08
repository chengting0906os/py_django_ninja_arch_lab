"""Global pytest configuration."""

import os
from pathlib import Path

from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from dotenv import load_dotenv
from ninja_extra.testing import TestAsyncClient
import pytest


os.environ.setdefault('NINJA_SKIP_REGISTRY', '1')

env_file = Path('.env') if Path('.env').exists() else Path('.env.example')
load_dotenv(env_file)

# Configure unique test database for each pytest worker
worker_id = os.environ.get('PYTEST_XDIST_WORKER', '')
testrun_uid = os.environ.get('PYTEST_XDIST_TESTRUNUID', '')

if testrun_uid and worker_id:
    test_db_suffix = f'{testrun_uid}_{worker_id}'
elif worker_id:
    test_db_suffix = f'{worker_id}'
else:
    test_db_suffix = f'{os.getpid()}'

os.environ.setdefault('TEST_DB_SUFFIX', test_db_suffix)


User = get_user_model()


class SessionTestAsyncClient(TestAsyncClient):
    """TestAsyncClient with session support for Django auth."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = SessionStore()
        self.session.create()

    def _build_request(self, *args, **kwargs):
        import os

        from django.contrib.auth.models import AnonymousUser

        mock = super()._build_request(*args, **kwargs)
        mock.session = self.session

        # Directly load user (this is a sync method, safe to use sync DB access)
        user_id = self.session.get('_auth_user_id')

        # Check if we're in async context
        if os.environ.get('DJANGO_ALLOW_ASYNC_UNSAFE'):
            # Already allowed, just query
            if user_id:
                try:
                    mock.user = User.objects.get(pk=user_id)
                except User.DoesNotExist:
                    mock.user = AnonymousUser()
            else:
                mock.user = AnonymousUser()
        else:
            # Temporarily allow async unsafe for this operation
            os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
            try:
                if user_id:
                    try:
                        mock.user = User.objects.get(pk=user_id)
                    except User.DoesNotExist:
                        mock.user = AnonymousUser()
                else:
                    mock.user = AnonymousUser()
            finally:
                del os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']

        return mock


@pytest.fixture(scope='session')
def api_instance():
    from src.platform.api import api

    return api


@pytest.fixture
def client(api_instance, db):
    """Test async client with API instance and database access."""
    client = SessionTestAsyncClient(api_instance)
    yield client
    # Close database connections after each test
    from django.db import connections

    for conn in connections.all():
        conn.close()


@pytest.fixture(scope='session', autouse=True)
def cleanup():
    yield
    os.environ.pop('NINJA_SKIP_REGISTRY', None)
    # Close all database connections at session end
    from django.db import connections

    for conn in connections.all():
        conn.close()

"""Global pytest configuration."""

import os
from pathlib import Path

from django.contrib.auth import get_user_model
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
    """TestAsyncClient with session support for Django auth.

    This custom client is necessary because:
    1. Django Ninja's TestAsyncClient doesn't support session by default
    2. We need session for Django's login() to work properly
    3. We need to load user from session for each request to support authentication
    """

    def __init__(self, *args, **kwargs):
        from django.contrib.sessions.backends.db import SessionStore

        super().__init__(*args, **kwargs)
        # Share same session across all requests
        self.session = SessionStore()
        self.session.create()

    def _build_request(self, *args, **kwargs):
        """Add shared session and user to the mock request."""
        import os

        from django.contrib.auth.models import AnonymousUser

        mock = super()._build_request(*args, **kwargs)
        # Use the same session instance for all requests
        mock.session = self.session

        # Load user from session (allow sync DB access in test)
        user_id = self.session.get('_auth_user_id')
        if user_id:
            # Temporarily allow async-unsafe operations for loading user
            os.environ['DJANGO_ALLOW_ASYNC_UNSAFE'] = 'true'
            try:
                mock.user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                mock.user = AnonymousUser()
            finally:
                del os.environ['DJANGO_ALLOW_ASYNC_UNSAFE']
        else:
            mock.user = AnonymousUser()

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

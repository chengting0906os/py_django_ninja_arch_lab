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
        from concurrent.futures import ThreadPoolExecutor

        from django.contrib.auth.models import AnonymousUser

        mock = super()._build_request(*args, **kwargs)
        # Use the same session instance for all requests
        mock.session = self.session

        # Load user from session using thread pool to avoid async context issues
        user_id = self.session.get('_auth_user_id')
        if user_id:

            def get_user_sync(pk):
                try:
                    return User.objects.get(pk=pk)
                except User.DoesNotExist:
                    return None

            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(get_user_sync, user_id)
                user = future.result()

            mock.user = user if user else AnonymousUser()
        else:
            mock.user = AnonymousUser()

        return mock


def pytest_configure(config):
    """Run migrations before tests when using --reuse-db."""
    from django.core.management import call_command

    # Only run if using reuse-db
    if config.getoption('--reuse-db', default=False):
        try:
            call_command('migrate', '--run-syncdb', verbosity=0)
        except Exception:
            pass  # First run might not have DB yet


@pytest.fixture(scope='session')
def api_instance():
    from src.platform.config.api import api

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

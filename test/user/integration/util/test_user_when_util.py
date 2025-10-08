"""When helpers for user integration tests."""

from ninja_extra.testing import TestAsyncClient

from src.platform.constant.route_constant import AUTH_LOGIN, USER_CREATE


async def when_create_user(client: TestAsyncClient, user_data: dict):
    """Create user via API."""
    return await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]


async def when_login(client: TestAsyncClient, email: str, password: str):
    """Attempt to login with given credentials."""
    login_data = {'email': email, 'password': password}
    return await client.post(AUTH_LOGIN, json=login_data)  # pyrefly: ignore[async-error]

"""Given helpers for user integration tests."""

from ninja_extra.testing import TestAsyncClient

from src.platform.constant.route_constant import USER_CREATE


async def given_user_exists(client: TestAsyncClient, email: str, password: str, role: str) -> int:
    """Create a user for testing and return user id."""
    user_data = {'email': email, 'password': password, 'role': role}
    response = await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 201, f'Failed to create user: {response.json()}'
    return response.json()['id']


def given_user_payload(email: str, password: str, role: str) -> dict:
    """Prepare user creation payload."""
    return {
        'email': email,
        'password': password,
        'role': role,
    }

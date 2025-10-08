from ninja_extra.testing import TestAsyncClient
import pytest

from src.platform.constant.route_constant import USER_CREATE
from test.util_constant import DEFAULT_PASSWORD, TEST_EMAIL


@pytest.mark.django_db(transaction=True)
class TestUserAPI:
    @pytest.mark.asyncio
    async def test_create_user(self, client: TestAsyncClient):
        email = TEST_EMAIL
        user_data = {
            'email': email,
            'password': DEFAULT_PASSWORD,
            'role': 'buyer',
        }
        response = await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]
        assert response.status_code == 201
        data = response.json()
        assert data['email'] == email
        assert data['role'] == 'buyer'
        assert 'id' in data
        assert 'password' not in data

    @pytest.mark.asyncio
    async def test_create_another_user(self, client: TestAsyncClient):
        user_data = {
            'email': 'another@example.com',
            'password': DEFAULT_PASSWORD,
            'role': 'seller',
        }
        response = await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]
        assert response.status_code == 201
        data = response.json()
        assert data['email'] == 'another@example.com'
        assert data['role'] == 'seller'

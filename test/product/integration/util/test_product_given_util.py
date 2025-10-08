"""Given helpers for product integration tests."""

from ninja_extra.testing import TestAsyncClient

from src.platform.constant.route_constant import AUTH_LOGIN, PRODUCT_CREATE, USER_CREATE


# User management helpers
async def given_seller_user_exists(client: TestAsyncClient, email: str, password: str) -> int:
    """Create a seller user for testing and return user id."""
    user_data = {'email': email, 'password': password, 'role': 'seller'}
    response = await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 201, f'Failed to create seller: {response.json()}'
    return response.json()['id']


async def given_buyer_user_exists(client: TestAsyncClient, email: str, password: str) -> int:
    """Create a buyer user for testing and return user id."""
    user_data = {'email': email, 'password': password, 'role': 'buyer'}
    response = await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 201, f'Failed to create buyer: {response.json()}'
    return response.json()['id']


async def given_logged_in_seller(client: TestAsyncClient, email: str, password: str) -> int:
    """Create and login a seller user via Django session, return user id."""
    user_id = await given_seller_user_exists(client, email, password)
    login_data = {'email': email, 'password': password}
    response = await client.post(AUTH_LOGIN, json=login_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 200, f'Failed to login: {response.json()}'
    return user_id


async def given_logged_in_buyer(client: TestAsyncClient, email: str, password: str) -> int:
    """Create and login a buyer user via Django session, return user id."""
    user_id = await given_buyer_user_exists(client, email, password)
    login_data = {'email': email, 'password': password}
    response = await client.post(AUTH_LOGIN, json=login_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 200, f'Failed to login: {response.json()}'
    return user_id


# Product management helpers
async def given_product_exists(
    client: TestAsyncClient,
    name: str,
    description: str,
    price: int,
    is_active: bool = True,
) -> int:
    """Create a product and return its ID."""
    product_data = {
        'name': name,
        'description': description,
        'price': price,
        'is_active': is_active,
    }
    response = await client.post(  # pyrefly: ignore[async-error]
        PRODUCT_CREATE, json=product_data
    )
    assert response.status_code == 201, f'Failed to create product: {response.json()}'
    return response.json()['id']


def given_product_payload(
    name: str, description: str, price: float, is_active: bool = True
) -> dict:
    """Prepare product creation payload."""
    return {
        'name': name,
        'description': description,
        'price': price,
        'is_active': is_active,
    }

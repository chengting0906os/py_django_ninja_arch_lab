"""Given helpers for order integration tests."""

from datetime import datetime, timezone
import re

from asgiref.sync import sync_to_async
from ninja_extra.testing import TestAsyncClient

from src.platform.models.order_model import OrderModel
from src.platform.models.product_model import ProductModel
from src.platform.constant.route_constant import AUTH_LOGIN, PRODUCT_CREATE, USER_CREATE
from test.util_constant import DEFAULT_PASSWORD


async def given_seller_with_product(
    client: TestAsyncClient,
    name: str,
    description: str,
    price: int,
    is_active: bool = True,
    status: str = 'available',
) -> tuple[int, int]:
    """Create a seller with a product and return (seller_id, product_id)."""
    # Create seller with safe email (remove spaces and special chars)

    safe_name = re.sub(r'[^a-z0-9_]', '_', name.lower())
    seller_email = f'seller_{safe_name}@test.com'

    seller_data = {
        'email': seller_email,
        'password': DEFAULT_PASSWORD,
        'role': 'seller',
    }
    response = await client.post(USER_CREATE, json=seller_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 201, f'Failed to create seller: {response.json()}'
    seller_id = response.json()['id']

    # Login as seller
    login_data = {'email': seller_email, 'password': DEFAULT_PASSWORD}
    response = await client.post(AUTH_LOGIN, json=login_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 200, f'Failed to login seller: {response.json()}'

    # Create product
    product_data = {
        'name': name,
        'description': description,
        'price': price,
        'is_active': is_active,
    }
    response = await client.post(PRODUCT_CREATE, json=product_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 201
    product_id = response.json()['id']

    # Update status if not available
    if status != 'available':
        from src.platform.models.product_model import ProductModel

        product = await sync_to_async(ProductModel.objects.get)(id=product_id)
        product.status = status
        await sync_to_async(product.save)()

    return seller_id, product_id


async def given_buyer_exists(client: TestAsyncClient, email: str, password: str) -> int:
    """Create a buyer user and return user id."""
    user_data = {'email': email, 'password': password, 'role': 'buyer'}
    response = await client.post(USER_CREATE, json=user_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 201
    return response.json()['id']


async def login_as(client: TestAsyncClient, email: str, password: str):
    """Login as user. Call this before each authenticated request."""
    login_data = {'email': email, 'password': password}
    response = await client.post(AUTH_LOGIN, json=login_data)  # pyrefly: ignore[async-error]
    assert response.status_code == 200, f'Failed to login: {response.json()}'


async def given_logged_in_as_buyer(client: TestAsyncClient, email: str, password: str) -> int:
    """Login as buyer (create if not exists), return user id."""
    # Try to create, ignore if already exists
    buyer_data = {'email': email, 'password': password, 'role': 'buyer'}
    response = await client.post(USER_CREATE, json=buyer_data)  # pyrefly: ignore[async-error]
    user_id = response.json()['id'] if response.status_code == 201 else 0

    # Login to authenticate
    await login_as(client, email, password)
    return user_id


async def given_logged_in_as_seller(client: TestAsyncClient, email: str, password: str) -> int:
    """Login as seller (create if not exists), return user id."""
    # Try to create, ignore if already exists
    seller_data = {'email': email, 'password': password, 'role': 'seller'}
    response = await client.post(USER_CREATE, json=seller_data)  # pyrefly: ignore[async-error]
    user_id = response.json()['id'] if response.status_code == 201 else 0

    # Login to authenticate
    await login_as(client, email, password)
    return user_id


async def given_users_exist(client: TestAsyncClient, users_data: list[dict]) -> dict[str, int]:
    """Create multiple users and return a mapping of email to user_id."""
    from src.platform.models.user_model import User as UserModel

    user_ids = {}
    for user in users_data:
        response = await client.post(USER_CREATE, json=user)  # pyrefly: ignore[async-error]
        assert response.status_code == 201, (
            f'Failed to create user {user["email"]}: {response.json()}'
        )
        user_id = response.json()['id']
        user_ids[user['email']] = user_id

        # Update user's first_name if name was provided
        if 'name' in user:
            user_model = await sync_to_async(UserModel.objects.get)(id=user_id)
            user_model.first_name = user['name']
            await sync_to_async(user_model.save)()

    return user_ids


async def given_products_exist(
    client: TestAsyncClient, seller_id: int, products_data: list[dict]
) -> list[int]:
    """Create multiple products for a seller and return list of product_ids."""

    product_ids = []

    for product in products_data:
        # Create product directly in DB to set status
        product_model = ProductModel(
            name=product['name'],
            description=product.get('description', f'{product["name"]} description'),
            price=product['price'],
            seller_id=seller_id,
            is_active=product.get('is_active', True),
            status=product.get('status', 'available'),
        )
        await sync_to_async(product_model.save)()
        product_ids.append(product_model.id)

    return product_ids


async def given_orders_exist(client: TestAsyncClient, orders_data: list[dict]) -> list[int]:
    """Create multiple orders and return list of order_ids."""

    order_ids = []

    for order in orders_data:
        # Handle paid_at
        paid_at = None
        if order.get('paid_at') == 'not_null':
            paid_at = datetime.now(timezone.utc)

        # Create order directly in DB
        order_model = OrderModel(
            buyer_id=order['buyer_id'],
            seller_id=order['seller_id'],
            product_id=order['product_id'],
            price=order['price'],
            status=order['status'],
            paid_at=paid_at,
        )
        await sync_to_async(order_model.save)()
        order_ids.append(order_model.id)

    return order_ids

"""When helpers for order integration tests."""

from ninja_extra.testing import TestAsyncClient

from src.platform.constant.route_constant import ORDER_CREATE


async def when_create_order(client: TestAsyncClient, product_id: int):
    """Create order via API using Django session authentication."""
    order_data = {'product_id': product_id}
    return await client.post(ORDER_CREATE, json=order_data)  # pyrefly: ignore[async-error]

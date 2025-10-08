"""Then helpers for order integration tests."""

from asgiref.sync import sync_to_async


def then_order_created_successfully(response, expected_price: int):
    """Assert order was created successfully."""
    assert response.status_code == 201, (
        f'Expected status 201, got {response.status_code}: {response.json()}'
    )
    response_json = response.json()
    assert response_json['price'] == expected_price
    assert response_json['status'] == 'pending_payment'
    assert response_json['created_at'] is not None
    assert response_json['paid_at'] is None
    assert 'id' in response_json
    assert response_json['id'] > 0


async def then_product_status_should_be(product_id: int, expected_status: str):
    """Assert product status matches expected value."""
    from src.driven_adapter.model.product_model import ProductModel

    product = await sync_to_async(ProductModel.objects.get)(id=product_id)
    assert product.status == expected_status, (
        f'Expected product status {expected_status}, got {product.status}'
    )


def then_order_creation_failed(response, expected_status: int):
    """Assert order creation failed with expected status."""
    assert response.status_code == expected_status, (
        f'Expected status {expected_status}, got {response.status_code}'
    )


def then_error_message_contains(response, expected_message: str):
    """Assert error message contains expected text."""
    response_data = response.json()
    assert 'detail' in response_data or 'message' in response_data, 'No error message in response'
    error_msg = response_data.get('detail') or response_data.get('message', '')
    assert expected_message in str(error_msg), (
        f'Expected "{expected_message}" in error message, got: {error_msg}'
    )


async def then_response_status_code_should_be(response, expected_status: int):
    """Assert response status code matches expected value."""
    assert response.status_code == expected_status, (
        f'Expected status {expected_status}, got {response.status_code}: {response.json()}'
    )


async def then_response_should_contain_orders(response, expected_count: int):
    """Assert response contains expected number of orders."""
    data = response.json()
    assert isinstance(data, list), f'Expected list, got {type(data)}'
    assert len(data) == expected_count, f'Expected {expected_count} orders, got {len(data)}'


async def then_orders_should_include(response, expected_orders: list[dict]):
    """Assert orders in response match expected values."""
    data = response.json()
    assert len(data) >= len(expected_orders), (
        f'Expected at least {len(expected_orders)} orders, got {len(data)}'
    )

    for expected in expected_orders:
        # Find matching order
        matching_order = None
        for order in data:
            # Match by product_name if available
            if order.get('product_name') == expected.get('product_name'):
                matching_order = order
                break

        assert matching_order is not None, (
            f'Could not find order with product_name={expected.get("product_name")}'
        )

        # Check all expected fields
        for key, value in expected.items():
            if key == 'paid_at':
                if value == 'not_null':
                    assert matching_order[key] is not None, f'Expected {key} to be not null'
                elif value is None:
                    assert matching_order[key] is None, (
                        f'Expected {key} to be null, got {matching_order[key]}'
                    )
            elif key == 'created_at':
                if value == 'not_null':
                    assert matching_order[key] is not None, f'Expected {key} to be not null'
            else:
                assert matching_order[key] == value, (
                    f'Expected {key}={value}, got {matching_order[key]}'
                )

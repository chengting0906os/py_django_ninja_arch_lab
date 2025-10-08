from typing import Any, Dict

import pytest
from ninja_extra.testing import TestAsyncClient

from src.platform.constant.route_constant import AUTH_LOGIN


def get_response_text(response) -> str:
    """Get text content from response (works for both Django and other responses)."""
    if hasattr(response, 'content'):
        return response.content.decode('utf-8')
    return getattr(response, 'text', '')


def extract_table_data(step) -> Dict[str, Any]:
    rows = step.data_table.rows
    headers = [cell.value for cell in rows[0].cells]
    values = [cell.value for cell in rows[1].cells]
    return dict(zip(headers, values, strict=True))


def extract_single_value(step, row_index: int = 0, col_index: int = 0) -> str:
    rows = step.data_table.rows
    return rows[row_index].cells[col_index].value


def login_user(client: TestAsyncClient, email: str, password: str) -> Any:
    """Helper function to login a user via Django session."""
    login_response = client.post(
        AUTH_LOGIN,
        json={'email': email, 'password': password},
    )
    if login_response.status_code != 200:
        message = (
            login_response.content.decode('utf-8')
            if hasattr(login_response, 'content')
            else getattr(login_response, 'reason_phrase', '')
        )
        pytest.fail(f'Login failed: {message}')

    return login_response


def assert_response_status(response, expected_status: int, message: str | None = None):
    """Helper function to assert response status code."""
    assert response.status_code == expected_status, (
        message
        or f'Expected {expected_status}, got {response.status_code}: {get_response_text(response)}'
    )


def create_user(
    client: TestAsyncClient, email: str, password: str, role: str
) -> Dict[str, Any] | None:
    """Helper function to create a user. Returns None if user already exists."""
    from src.platform.constant.route_constant import USER_CREATE

    user_data = {
        'email': email,
        'password': password,
        'role': role,
    }
    response = client.post(USER_CREATE, json=user_data)
    if response.status_code == 201:
        return response.json()
    elif response.status_code == 400:  # User already exists
        return None
    else:
        assert_response_status(response, 201, f'Failed to create {role} user')
        return None


def create_product(
    client: TestAsyncClient, name: str, description: str, price: int, is_active: bool = True
) -> Dict[str, Any]:
    """Helper function to create a product."""
    from src.platform.constant.route_constant import PRODUCT_BASE

    product_data = {
        'name': name,
        'description': description,
        'price': price,
        'is_active': is_active,
    }
    response = client.post(PRODUCT_BASE, json=product_data)
    assert_response_status(response, 201, 'Failed to create product')
    return response.json()

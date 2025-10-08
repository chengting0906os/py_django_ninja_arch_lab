"""Then helpers for product integration tests."""


def then_response_successful(response, expected_status: int = 200):
    """Assert response was successful."""
    assert response.status_code == expected_status, (
        f'Expected status {expected_status}, got {response.status_code}: {response.json()}'
    )


def then_error_message_contains(response, expected_message: str):
    """Assert error message contains expected text."""
    response_data = response.json()
    assert 'detail' in response_data or 'message' in response_data, 'No error message in response'
    error_msg = response_data.get('detail') or response_data.get('message', '')
    assert expected_message in str(error_msg), (
        f'Expected "{expected_message}" in error message, got: {error_msg}'
    )

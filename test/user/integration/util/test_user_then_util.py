"""Then helpers for user integration tests."""


def then_user_created_successfully(response, user_data: dict):
    """Assert user was created successfully."""
    assert response.status_code == 201, (
        f'Expected status 201, got {response.status_code}: {response.json()}'
    )
    response_json = response.json()
    assert response_json['email'] == user_data['email']
    assert response_json['role'] == user_data['role']
    assert 'id' in response_json
    assert response_json['id'] > 0


def then_user_creation_failed(response, expected_status: int):
    """Assert user creation failed with expected status."""
    assert response.status_code == expected_status, (
        f'Expected status {expected_status}, got {response.status_code}'
    )


def then_login_successful(response):
    """Assert login was successful."""
    assert response.status_code == 200, (
        f'Expected status 200, got {response.status_code}: {response.json()}'
    )


def then_login_failed(response, expected_status: int):
    """Assert login failed with expected status."""
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


def then_user_info_matches(response, email: str, role: str):
    """Assert user info in response matches expected values."""
    response_data = response.json()
    assert response_data['email'] == email, (
        f'Expected email {email}, got {response_data.get("email")}'
    )
    assert response_data['role'] == role, f'Expected role {role}, got {response_data.get("role")}'

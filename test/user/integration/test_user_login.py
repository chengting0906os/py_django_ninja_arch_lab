"""User login integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from test.user.integration.util import (
    given_user_exists,
    then_error_message_contains,
    then_login_failed,
    then_login_successful,
    then_user_info_matches,
    when_login,
)
from test.util_constant import DEFAULT_PASSWORD, TEST_BUYER_EMAIL, TEST_SELLER_EMAIL


@pytest.mark.django_db(transaction=True)
class TestUserLogin:
    @pytest.mark.asyncio
    async def test_successful_buyer_login(self, client: TestAsyncClient):
        """Test successful buyer login."""
        # Given
        await given_user_exists(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD, 'buyer')

        # When
        response = await when_login(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD)

        # Then
        then_login_successful(response)
        then_user_info_matches(response, TEST_BUYER_EMAIL, 'buyer')

    @pytest.mark.asyncio
    async def test_successful_seller_login(self, client: TestAsyncClient):
        """Test successful seller login."""
        # Given
        await given_user_exists(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD, 'seller')

        # When
        response = await when_login(client, TEST_SELLER_EMAIL, DEFAULT_PASSWORD)

        # Then
        then_login_successful(response)
        then_user_info_matches(response, TEST_SELLER_EMAIL, 'seller')

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, client: TestAsyncClient):
        """Test login with wrong password should return 400."""
        # Given
        await given_user_exists(client, TEST_BUYER_EMAIL, DEFAULT_PASSWORD, 'buyer')

        # When
        response = await when_login(client, TEST_BUYER_EMAIL, 'WrongPass')

        # Then
        then_login_failed(response, 400)
        then_error_message_contains(response, 'LOGIN_BAD_CREDENTIALS')

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email(self, client: TestAsyncClient):
        """Test login with non-existent email should return 400."""
        # When
        response = await when_login(client, 'nonexist@test.com', DEFAULT_PASSWORD)

        # Then
        then_login_failed(response, 400)
        then_error_message_contains(response, 'LOGIN_BAD_CREDENTIALS')

"""User creation integration tests using given-when-then pattern."""

from ninja_extra.testing import TestAsyncClient
import pytest

from test.user.integration.util import (
    given_user_payload,
    then_user_created_successfully,
    then_user_creation_failed,
    when_create_user,
)


@pytest.mark.django_db(transaction=True)
class TestUserCreation:
    @pytest.mark.asyncio
    async def test_create_buyer_user(self, client: TestAsyncClient):
        """Test creating a new buyer user."""
        # Given
        user_data = given_user_payload('test@example.com', 'P@ssw0rd', 'buyer')

        # When
        response = await when_create_user(client, user_data)

        # Then
        then_user_created_successfully(response, user_data)

    @pytest.mark.asyncio
    async def test_create_seller_user(self, client: TestAsyncClient):
        """Test creating a new seller user."""
        # Given
        user_data = given_user_payload('seller@example.com', 'P@ssw0rd', 'seller')

        # When
        response = await when_create_user(client, user_data)

        # Then
        then_user_created_successfully(response, user_data)

    @pytest.mark.asyncio
    async def test_create_user_with_invalid_role(self, client: TestAsyncClient):
        """Test creating a user with invalid role."""
        # Given
        user_data = given_user_payload('test@example.com', 'P@ssw0rd', 'wrong_user')

        # When
        response = await when_create_user(client, user_data)

        # Then
        then_user_creation_failed(response, 400)

    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, client: TestAsyncClient):
        """Test creating a user with duplicate email."""
        # Given
        user_data = given_user_payload('duplicate@example.com', 'P@ssw0rd', 'buyer')
        await when_create_user(client, user_data)

        # When
        response = await when_create_user(client, user_data)

        # Then
        then_user_creation_failed(response, 400)

import pytest


@pytest.fixture
def product_state(db):
    # Clean up products and users before each test
    from src.driven_adapter.model.product_model import ProductModel
    from src.driven_adapter.model.user_model import User

    ProductModel.objects.all().delete()
    User.objects.all().delete()

    yield {}

    # Clean up after test
    ProductModel.objects.all().delete()
    User.objects.all().delete()

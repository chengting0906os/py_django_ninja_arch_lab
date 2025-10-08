"""Central Ninja Extra API instance."""

from ninja_extra import NinjaExtraAPI

from src.driving_adapter.http_controller.order_controller import OrderController
from src.driving_adapter.http_controller.product_controller import ProductController
from src.driving_adapter.http_controller.user_controller import UserController
from src.platform.exception.exception_handler import setup_exception_handlers


# Create API (injector is configured via NINJA_EXTRA settings)
api = NinjaExtraAPI()

# Register controllers
api.register_controllers(UserController, ProductController, OrderController)
setup_exception_handlers(api)

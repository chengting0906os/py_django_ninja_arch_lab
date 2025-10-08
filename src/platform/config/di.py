"""Dependency injection configuration for application use cases."""

from __future__ import annotations

from injector import Binder, Module, provider, singleton

from src.app.interface.i_email_dispatcher import IEmailDispatcher
from src.app.interface.i_order_repo import IOrderRepo
from src.app.interface.i_product_repo import IProductRepo
from src.app.interface.i_user_repo import IUserRepo
from src.app.use_case.order.cancel_order_use_case import CancelOrderUseCase
from src.app.use_case.order.create_order_use_case import CreateOrderUseCase
from src.app.use_case.order.get_order_use_case import GetOrderUseCase
from src.app.use_case.order.list_order_use_case import ListOrdersUseCase
from src.app.use_case.order.mock_order_payment_use_case import MockOrderPaymentUseCase
from src.app.use_case.product.create_product_use_case import CreateProductUseCase
from src.app.use_case.product.delete_product_use_case import DeleteProductUseCase
from src.app.use_case.product.get_product_use_case import GetProductUseCase
from src.app.use_case.product.list_product_use_case import ListProductUseCase
from src.app.use_case.product.update_product_use_case import UpdateProductUseCase
from src.driven_adapter.repo.order_repo_impl import OrderRepoImpl
from src.driven_adapter.repo.product_repo_impl import ProductRepoImpl
from src.driven_adapter.repo.user_repo_impl import UserRepoImpl
from src.platform.notification.mock_email_dispatcher import (
    MockEmailDispatcher,
    get_mock_email_dispatcher,
)


class CoreInfrastructureModule(Module):
    """Provide core infrastructure dependencies."""

    @singleton
    @provider
    def provide_email_dispatcher(self) -> IEmailDispatcher:
        dispatcher: MockEmailDispatcher = get_mock_email_dispatcher()
        return dispatcher

    @singleton
    @provider
    def provide_user_repo(self) -> IUserRepo:
        return UserRepoImpl()

    @singleton
    @provider
    def provide_product_repo(self) -> IProductRepo:
        return ProductRepoImpl()

    @singleton
    @provider
    def provide_order_repo(self) -> IOrderRepo:
        return OrderRepoImpl()


class ProductUseCaseModule(Module):
    """Bind product-related use cases."""

    @provider
    def provide_create_product_use_case(
        self,
        product_repo: IProductRepo,
    ) -> CreateProductUseCase:
        return CreateProductUseCase(product_repo)

    @provider
    def provide_get_product_use_case(
        self,
        product_repo: IProductRepo,
    ) -> GetProductUseCase:
        return GetProductUseCase(product_repo)

    @provider
    def provide_list_product_use_case(
        self,
        product_repo: IProductRepo,
    ) -> ListProductUseCase:
        return ListProductUseCase(product_repo)

    @provider
    def provide_update_product_use_case(
        self,
        product_repo: IProductRepo,
    ) -> UpdateProductUseCase:
        return UpdateProductUseCase(product_repo)

    @provider
    def provide_delete_product_use_case(
        self,
        product_repo: IProductRepo,
    ) -> DeleteProductUseCase:
        return DeleteProductUseCase(product_repo)


class OrderUseCaseModule(Module):
    """Bind order-related use cases."""

    @provider
    def provide_create_order_use_case(
        self,
        email_dispatcher: IEmailDispatcher,
        user_repo: IUserRepo,
        product_repo: IProductRepo,
        order_repo: IOrderRepo,
    ) -> CreateOrderUseCase:
        return CreateOrderUseCase(email_dispatcher, user_repo, product_repo, order_repo)

    @provider
    def provide_get_order_use_case(
        self,
        order_repo: IOrderRepo,
    ) -> GetOrderUseCase:
        return GetOrderUseCase(order_repo)

    @provider
    def provide_list_orders_use_case(
        self,
        order_repo: IOrderRepo,
    ) -> ListOrdersUseCase:
        return ListOrdersUseCase(order_repo)

    @provider
    def provide_cancel_order_use_case(
        self,
        email_dispatcher: IEmailDispatcher,
        user_repo: IUserRepo,
        product_repo: IProductRepo,
        order_repo: IOrderRepo,
    ) -> CancelOrderUseCase:
        return CancelOrderUseCase(email_dispatcher, user_repo, product_repo, order_repo)

    @provider
    def provide_mock_order_payment_use_case(
        self,
        order_repo: IOrderRepo,
        product_repo: IProductRepo,
    ) -> MockOrderPaymentUseCase:
        return MockOrderPaymentUseCase(order_repo, product_repo)


class ApplicationModule(Module):
    """Root module installing all dependency sub-modules."""

    def configure(self, binder: Binder) -> None:
        binder.install(CoreInfrastructureModule())
        binder.install(ProductUseCaseModule())
        binder.install(OrderUseCaseModule())

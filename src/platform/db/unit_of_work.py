"""Unit of Work pattern implementation."""

from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.platform.db.db_setting import get_async_session


if TYPE_CHECKING:
    from src.app.interface.i_order_repo import IOrderRepo
    from src.app.interface.i_product_repo import IProductRepo
    from src.app.interface.i_user_repo import IUserRepo


class AbstractUnitOfWork(abc.ABC):
    products: IProductRepo
    orders: IOrderRepo
    users: IUserRepo

    async def __aenter__(self) -> AbstractUnitOfWork:
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def __aenter__(self):
        from src.driven_adapter.repo.order_repo_impl import OrderRepoImpl
        from src.driven_adapter.repo.product_repo_impl import ProductRepoImpl
        from src.driven_adapter.repo.user_repo_impl import UserRepoImpl

        self.products = ProductRepoImpl(self.session)
        self.orders = OrderRepoImpl(self.session)
        self.users = UserRepoImpl(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    # pyrefly: ignore  # bad-override
    async def _commit(self):
        await self.session.commit()

    # pyrefly: ignore  # bad-override
    async def rollback(self):
        await self.session.rollback()


def get_unit_of_work(session: AsyncSession = Depends(get_async_session)) -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session)

from uuid import UUID

from sqlalchemy import select, text, func, or_, and_
from sqlalchemy.orm import subqueryload, joinedload

from src.models import tables
from src.services.repository.base import BaseRepository


class AttemptRepo(BaseRepository[tables.Attempt]):
    table = tables.Attempt

    async def get_first(self, user_id: UUID, test_id: UUID) -> tables.Attempt:
        stmt = select(self.table).filter_by(user_id=user_id, test_id=test_id).order_by(text("created_at")).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def search(
            self,
            query: str,
            fields: list[str],
            limit: int = 100,
            offset: int = 0,
            order_by: str = "created_at",
            **kwargs
    ) -> list[tables.Vacancy]:
        return await self.__get_range(
            query=query,
            fields=fields,
            limit=limit,
            offset=offset,
            order_by=order_by,
            **kwargs
        )

    async def __get_range(
            self,
            *,
            query: str = None,
            fields: list[str] = None,
            limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            **kwargs
    ) -> list[tables.Vacancy]:
        stmt = (
            select(
                self.table,
            )
            .order_by(text(order_by))
            .limit(limit)
            .offset(offset)
        )

        # Фильтры kwargs
        stmt = stmt.where(
            and_(*[getattr(self.table, field) == value for field, value in kwargs.items()])
        )

        # Поиск
        if query and fields:
            stmt = stmt.where(
                or_(*[getattr(self.table, field).ilike(f"%{query}%") for field in fields])
            )

        return await self._session.execute(stmt).scalars().all()

    async def get_all(
            self, limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            as_full: bool = False,
            **kwargs
    ) -> list[tables.Attempt]:
        req = select(self.table).filter_by(**kwargs)
        if as_full:
            req = req.options(joinedload(self.table.test))

        result = (await self._session.execute(req.order_by(text(order_by)).limit(limit).offset(offset))).unique()
        return result.scalars().all()
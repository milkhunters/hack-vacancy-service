from sqlalchemy import select, text, func, or_, and_
from sqlalchemy.orm import subqueryload

from src.models import tables
from .base import BaseRepository


class VacancyRepo(BaseRepository[tables.Vacancy]):
    table = tables.Vacancy

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

    async def get_all(
            self, limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            **kwargs
    ) -> list[tables.Vacancy]:
        return await self.__get_range(
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
        result = await self._session.execute(stmt)
        return result.scalars().all()

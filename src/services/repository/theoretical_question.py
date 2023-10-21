from sqlalchemy import select, text
from sqlalchemy.orm import joinedload

from src.models import tables
from src.services.repository.base import BaseRepository


class TheoreticalQuestionRepo(BaseRepository[tables.TheoreticalQuestion]):
    table = tables.TheoreticalQuestion

    async def get(self, as_full: bool = False, **kwargs) -> tables.TheoreticalQuestion | None:
        req = select(self.table).filter_by(**kwargs)
        if as_full:
            req = req.options(joinedload(self.table.answer_options))
        return (await self._session.execute(req)).scalars().first()

    async def get_all(
            self, limit: int = 100,
            offset: int = 0,
            order_by: str = "id",
            as_full: bool = False,
            **kwargs
    ) -> list[tables.TheoreticalQuestion]:
        req = select(self.table).filter_by(**kwargs)
        if as_full:
            req = req.options(joinedload(self.table.answer_options))

        result = (await self._session.execute(req.order_by(text(order_by)).limit(limit).offset(offset))).unique()
        return result.scalars().all()
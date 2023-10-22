from uuid import UUID

from sqlalchemy import select, text, func, or_, and_, case
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

    async def get_successful_requests(self) -> list[dict]:
        stmt = (
            select(
                self.table.user_id.label("user_id"),

                tables.Vacancy.id.label("vacancy_id"),
                tables.Vacancy.title.label("vacancy_title"),
                tables.Vacancy.state.label("vacancy_state"),
                tables.Vacancy.type.label("vacancy_type"),
                tables.Vacancy.created_at.label("vacancy_created_at"),

                tables.Testing.id.label("testing_id"),
                tables.Testing.title.label("testing_title"),

                self.table.percent.label("percent"),
            )
            .join(tables.Testing, self.table.test_id == tables.Testing.id)
            .join(tables.Vacancy, tables.Testing.vacancy_id == tables.Vacancy.id)
            .where(
                self.table.percent >= tables.Testing.correct_percent
            )
        )

        stmt2 = (
            select(
                tables.Vacancy.id.label("vacancy_id"),
                func.count(tables.Testing.id).label("count")
            )
            .join(tables.Testing, tables.Testing.vacancy_id == tables.Vacancy.id)
            .group_by(tables.Vacancy.id)
        )

        # Выполнение запроса Attempt
        attempts_result = await self.session.execute(stmt)
        attempts_records = attempts_result.fetchall()

        # Выполнение запроса Vacancy
        vacancies_result = await self.session.execute(stmt2)
        vacancies_records = vacancies_result.fetchall()

        vacancies_test_count = {}
        for record in vacancies_records:
            vacancies_test_count[record.vacancy_id] = record.count

        # Группировка по пользователю и вакансии
        user_data = {}

        for record in attempts_records:
            key = (record.user_id, record.vacancy_id)

            if user_data.get(key) is None:
                user_data[key] = [record]
            else:
                user_data[key].append(record)

        # Выборка успешных попыток
        response = []
        for key, records in user_data.items():
            row = {
                "user_id": key[0],
                "vacancy_id": key[1],
                "vacancy_title": records[0].vacancy_title,
                "vacancy_state": records[0].vacancy_state,
                "vacancy_type": records[0].vacancy_type,
                "vacancy_created_at": records[0].vacancy_created_at,
                "testings": []
            }
            testings = {}

            for record in records:
                if testings.get(record.testing_id) is None:
                    testings[record.testing_id] = {
                        "testing_id": record.testing_id,
                        "testing_title": record.testing_title,
                        "percent": record.percent
                    }
                else:
                    testings[record.testing_id]["percent"] = max(
                        testings[record.testing_id]["percent"],
                        record.percent
                    )

            row["testings"] = list(testings.values())
            if len(row["testings"]) == vacancies_test_count[row["vacancy_id"]]:
                response.append(row)

        return response

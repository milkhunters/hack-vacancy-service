import uuid
from typing import Literal

from src import exceptions
from src.models import schemas
from src.models.permission import Permission
from src.models.auth import BaseUser
from src.models.state import VacancyState, UserState
from src.services.auth.filters import state_filter
from src.services.auth.filters import permission_filter
from src.services.repository import FileRepo
from src.services.repository import VacancyRepo
from src.utils.s3 import S3Storage


class VacancyApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            vacancy_repo: VacancyRepo,
            file_repo: FileRepo,
            file_storage: S3Storage

    ):
        self._current_user = current_user
        self._repo = vacancy_repo
        self._file_repo = file_repo
        self._file_storage = file_storage

    async def get_vacancies(
            self,
            state: VacancyState,
            page: int = 1,
            per_page: int = 10,
            order_by: Literal["title", "updated_at", "created_at"] = "created_at",
            query: str = None
    ) -> list[schemas.VacancySmall]:
        """
        Получить список вакансий

        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1, но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: поисковый запрос (если необходим)
        :param state: статус вакансии (по умолчанию только открытые)
        :return:

        """

        if page < 1:
            raise exceptions.NotFound("Страница не найдена")
        if per_page < 1:
            raise exceptions.BadRequest("Неверное количество элементов на странице")

        if (
                state != VacancyState.OPENED and
                Permission.GET_PRIVATE_VACANCY.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете получить список приватных вакансий")

        if (
                state == VacancyState.OPENED and
                Permission.GET_PUBLIC_VACANCY.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете получить список публичных вакансий")

        per_page_limit = 40

        # Подготовка входных данных
        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        # Выполнение запроса
        if query:
            vacancies = await self._repo.search(
                query=query,
                fields=["title", "content"],
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"state": state} if state else {},
            )
        else:
            vacancies = await self._repo.get_all(
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"state": state} if state else {},
            )
        return [schemas.VacancySmall.model_validate(vacancy) for vacancy in vacancies]

    async def get_vacancy(self, vacancy_id: uuid.UUID) -> schemas.Vacancy:
        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        if (
                vacancy.state != VacancyState.OPENED and
                Permission.GET_PRIVATE_VACANCY.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вакансия не найдена")

        if (
                vacancy.state == VacancyState.OPENED and
                Permission.GET_PUBLIC_VACANCY.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете получить публичную вакансию")

        return schemas.Vacancy.model_validate(vacancy)

    @permission_filter(Permission.CREATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def create_vacancy(self, data: schemas.VacancyCreate) -> schemas.Vacancy:
        vacancy = await self._repo.create(
            **data.model_dump()
        )
        return schemas.Vacancy.model_validate(vacancy)

    @permission_filter(Permission.UPDATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def update_vacancy(self, vacancy_id: uuid.UUID, data: schemas.VacancyUpdate) -> None:
        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        await self._repo.update(vacancy_id, **data.model_dump(exclude_unset=True))

    @permission_filter(Permission.DELETE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def delete_vacancy(self, vacancy_id: uuid.UUID) -> None:
        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")
        # todo
        await self._repo.delete(id=vacancy_id)

    @permission_filter(Permission.UPDATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def get_vacancy_files(self, vacancy_id: uuid.UUID) -> list[schemas.VacancyFileItem]:
        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        files = await self._file_repo.get_all(vacancy_id=vacancy_id, is_uploaded=True)

        resp = []
        for file in files:
            url = self._file_storage.generate_download_public_url(
                file_path=f"{vacancy.id}/{file.id}",
                content_type=file.content_type,
                rcd="inline",
                filename=file.filename
            )
            resp.append(schemas.VacancyFileItem(
                url=url,
                **schemas.VacancyFile.model_validate(file).model_dump(exclude={"is_uploaded", "vacancy_id"})
            ))

        return resp

    async def get_vacancy_file(
            self,
            vacancy_id: uuid.UUID,
            file_id: uuid.UUID,
            download: bool
    ) -> schemas.VacancyFileItem:

        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        if (
                vacancy.state != VacancyState.OPENED and
                Permission.GET_PRIVATE_VACANCY.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы закрытых вакансий")

        if (
                vacancy.state == VacancyState.OPENED and
                Permission.GET_PUBLIC_VACANCY.value not in self._current_user.permissions
        ):
            raise exceptions.AccessDenied("Вы не можете просматривать файлы публичных вакансий")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if not file.is_uploaded:
            raise exceptions.NotFound("Файл не загружен")

        url = self._file_storage.generate_download_public_url(
            file_path=f"{vacancy.id}/{file.id}",
            content_type=file.content_type,
            rcd="attachment" if download else "inline",
            filename=file.filename
        )

        return schemas.VacancyFileItem(
            url=url,
            **schemas.VacancyFile.model_validate(file).model_dump(exclude={"is_uploaded", "vacancy_id"})
        )

    @permission_filter(Permission.UPDATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def upload_vacancy_file(
            self,
            vacancy_id: uuid.UUID,
            data: schemas.VacancyFileCreate
    ) -> schemas.VacancyFileUpload:

        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        file = await self._file_repo.create(
            filename=data.filename,
            vacancy_id=vacancy_id,
            content_type=data.content_type.value
        )

        url = schemas.PreSignedPostUrl.model_validate(
            await self._file_storage.generate_upload_url(
                file_path=f"{vacancy.id}/{file.id}",
                content_type=data.content_type.value,
                content_length=(1, 100 * 1024 * 1024),  # 100mb
                expires_in=30 * 60  # 30 min
            )
        )

        return schemas.VacancyFileUpload(
            file_id=file.id,
            upload_url=url
        )

    @permission_filter(Permission.UPDATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def confirm_vacancy_file_upload(
            self,
            vacancy_id: uuid.UUID,
            file_id: uuid.UUID
    ) -> None:

        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if file.vacancy_id != vacancy_id:
            raise exceptions.BadRequest("Файл не принадлежит статье")

        if file.is_uploaded:
            raise exceptions.BadRequest("Файл уже загружен")

        info = await self._file_storage.info(file_path=f"{vacancy_id}/{file_id}")
        if not info:
            raise exceptions.NotFound("Файл не загружен")

        await self._file_repo.update(id=file_id, is_uploaded=True)

    @permission_filter(Permission.UPDATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def delete_vacancy_file(self, vacancy_id: uuid.UUID, file_id: uuid.UUID) -> None:
        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if file.vacancy_id != vacancy_id:
            raise exceptions.BadRequest("Файл не принадлежит статье")

        if not file.is_uploaded:
            raise exceptions.BadRequest("Файл не загружен")

        if vacancy.poster == file_id:
            await self._repo.update(id=vacancy_id, poster=None)

        await self._file_storage.delete(file_path=f"{vacancy_id}/{file_id}")
        await self._file_repo.delete(id=file_id)

    @permission_filter(Permission.UPDATE_VACANCY)
    @state_filter(UserState.ACTIVE)
    async def set_vacancy_poster(self, vacancy_id: uuid.UUID, file_id: uuid.UUID) -> None:
        vacancy = await self._repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound("Вакансия не найдена")

        file = await self._file_repo.get(id=file_id)
        if not file:
            raise exceptions.NotFound("Файл не найден")

        if file.vacancy_id != vacancy_id:
            raise exceptions.BadRequest("Файл не принадлежит статье")

        if not file.is_uploaded:
            raise exceptions.BadRequest("Файл не загружен")

        if vacancy.poster == file_id:
            raise exceptions.BadRequest("Этот файл уже является постером статьи")

        await self._repo.update(id=vacancy_id, poster=file_id)

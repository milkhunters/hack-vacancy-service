import uuid
from typing import Literal

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.models.state import VacancyState
from src.services import ServiceFactory
from src.views import VacancyResponse, VacanciesResponse
from src.views.vacancy import VacancyFilesResponse, VacancyFileUploadResponse, VacancyFileResponse

router = APIRouter()


@router.get("/list", response_model=VacanciesResponse, status_code=http_status.HTTP_200_OK)
async def get_vacancy_list(
        state: VacancyState,
        page: int = 1,
        per_page: int = 10,
        order_by: Literal["title", "updated_at", "created_at"] = "created_at",
        query: str = None,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить список вакансий

    Требуемое состояние: -

    Требуемые права доступа: GET_PRIVATE_VACANCY / GET_PUBLIC_VACANCY
    """
    return VacanciesResponse(
        content=await services.vacancy.get_vacancies(
            state=state,
            page=page,
            per_page=per_page,
            order_by=order_by,
            query=query
        )
    )


@router.post("/new", response_model=VacancyResponse, status_code=http_status.HTTP_201_CREATED)
async def new_vacancy(vacancy: schemas.VacancyCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать экзамен

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_SELF_ARTICLES

    Максимальный размер статьи - 32000 символов
    """
    return VacancyResponse(content=await services.vacancy.create_vacancy(vacancy))


@router.get("/{vacancy_id}", response_model=VacancyResponse, status_code=http_status.HTTP_200_OK)
async def get_vacancy(vacancy_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить экзамен по id

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_ARTICLES / GET_PRIVATE_ARTICLES / GET_SELF_ARTICLES
    """
    return VacancyResponse(content=await services.vacancy.get_vacancy(vacancy_id))


@router.put("/{vacancy_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_vacancy(
        vacancy_id: uuid.UUID,
        data: schemas.VacancyUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить экзамен по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_VACANCY

    """
    await services.vacancy.update_vacancy(vacancy_id, data)


@router.delete("/{vacancy_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_vacancy(vacancy_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить экзамен по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_VACANCY

    """
    await services.vacancy.delete_vacancy(vacancy_id)


@router.get("/files/{vacancy_id}", response_model=VacancyFilesResponse, status_code=http_status.HTTP_200_OK)
async def get_vacancy_files(vacancy_id: uuid.UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить список файлов статьи по id

    Требуемое состояние: -

    Требуемые права доступа: UPDATE_VACANCY
    """
    return VacancyFilesResponse(content=await services.vacancy.get_vacancy_files(vacancy_id))


@router.get("/files/{vacancy_id}/{file_id}", response_model=VacancyFileResponse, status_code=http_status.HTTP_200_OK)
async def get_vacancy_file(
        vacancy_id: uuid.UUID,
        file_id: uuid.UUID,
        download: bool = False,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить файл статьи по id

    Требуемое состояние: -

    Требуемые права доступа: GET_PUBLIC_VACANCY / GET_PRIVATE_VACANCY
    """
    return VacancyFileResponse(content=await services.vacancy.get_vacancy_file(vacancy_id, file_id, download))


@router.post(
    "/files/{vacancy_id}",
    response_model=VacancyFileUploadResponse,
    status_code=http_status.HTTP_200_OK
)
async def upload_vacancy_file(
        vacancy_id: uuid.UUID,
        data: schemas.VacancyFileCreate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Загрузить файл статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_VACANCY

    """
    return VacancyFileUploadResponse(content=await services.vacancy.upload_vacancy_file(vacancy_id, data))


@router.post("/files/{vacancy_id}/{file_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def confirm_vacancy_file(
        vacancy_id: uuid.UUID,
        file_id: uuid.UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Подтвердить загрузку файла статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_VACANCY
    """
    await services.vacancy.confirm_vacancy_file_upload(vacancy_id, file_id)


@router.delete("/files/{vacancy_id}/{file_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_vacancy_file(
        vacancy_id: uuid.UUID,
        file_id: uuid.UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Удалить файл статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_VACANCY
    """
    await services.vacancy.delete_vacancy_file(vacancy_id, file_id)


@router.post("/poster", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def set_poster(
        vacancy_id: uuid.UUID,
        file_id: uuid.UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Установить постер статьи по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_VACANCY
    """
    await services.vacancy.set_vacancy_poster(vacancy_id, file_id)

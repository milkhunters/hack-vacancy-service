from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory
from src.views.testing import TestingsResponse
from src.views.testing import TestingResponse
from src.views.testing import AttemptsTestResponse

router = APIRouter()


@router.get("/list", response_model=TestingsResponse, status_code=http_status.HTTP_200_OK)
async def get_testing_list(vacancy_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить список тестирований вакансии

    Требуемое состояние: Active

    Требуемые права доступа: GET_TESTING
    """
    return TestingsResponse(
        content=await services.testing.get_testings(vacancy_id)
    )


@router.post("/new", response_model=TestingResponse, status_code=http_status.HTTP_201_CREATED)
async def new_testing(vacancy_id: UUID, data: schemas.TestingCreate, services: ServiceFactory = Depends(get_services)):
    """
    Создать тестирование

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_TESTING

    Максимальный размер контента - 32000 символов

    Максимальный размер названия - 255 символов
    """
    return TestingResponse(content=await services.testing.create_testing(vacancy_id, data))

@router.get("/attempts", response_model=AttemptsTestResponse, status_code=http_status.HTTP_200_OK)
async def get_self_attempts(
        page: int = 1,
        per_page: int = 10,
        order_by: Literal["title", "created_at"] = "created_at",
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить свои общие результаты тестирования

    Требуемое состояние: ACTIVE

    Требуемые права доступа: GET_SELF_TEST_RESULTS

    """
    return AttemptsTestResponse(
        content=await services.testing.get_test_attempts(
            page=page,
            per_page=per_page,
            order_by=order_by
        )
    )


@router.get("/{testing_id}/attempts", response_model=AttemptsTestResponse, status_code=http_status.HTTP_200_OK)
async def get_self_testing_attempts(
        testing_id: UUID,
        page: int = 1,
        per_page: int = 10,
        order_by: Literal["title", "created_at"] = "created_at",
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить свои результаты тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: GET_SELF_TEST_RESULTS

    """
    return AttemptsTestResponse(
        content=await services.testing.get_test_attempts(
            testing_id=testing_id,
            page=page,
            per_page=per_page,
            order_by=order_by
        )
    )


@router.get(
    "/attempts/{user_id}",
    response_model=AttemptsTestResponse,
    status_code=http_status.HTTP_200_OK
)
async def get_user_attempts(
        page: int = 1,
        per_page: int = 10,
        order_by: Literal["title", "created_at"] = "created_at",
        query: str = None,
        user_id: UUID = None,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить результаты тестирования пользователя по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: GET_USER_TEST_RESULTS

    """
    return AttemptsTestResponse(
        content=await services.testing.get_user_attempts(
            page=page,
            per_page=per_page,
            order_by=order_by,
            query=query,
            user_id=user_id
        )
    )


@router.delete("/{testing_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_testing(testing_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Удалить тестирование по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_TESTING

    """
    await services.testing.delete_testing(testing_id)


@router.get("/{testing_id}", response_model=TestingResponse, status_code=http_status.HTTP_200_OK)
async def get_testing(testing_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Получить тестирование по id

    Требуемое состояние: - Active

    Требуемые права доступа: GET_TESTING
    """
    return TestingResponse(content=await services.testing.get_testing(testing_id))


@router.put("/{testing_id}", response_model=None, status_code=http_status.HTTP_204_NO_CONTENT)
async def update_testing(
        testing_id: UUID,
        data: schemas.TestingUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить тестирование по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    await services.testing.update_testing(testing_id, data)

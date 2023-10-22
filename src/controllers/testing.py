from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_status

from src.dependencies.services import get_services
from src.models import schemas
from src.services import ServiceFactory
from src.views.request import ApprovedRequestsResponse
from src.views.testing import TestingsResponse
from src.views.testing import PracticalQuestionsResponse
from src.views.testing import TheoreticalQuestionsResponse
from src.views.testing import AttemptTestResponse
from src.views.testing import PracticalQuestionResponse
from src.views.testing import TheoreticalQuestionResponse
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
    "/approved/users",
    response_model=ApprovedRequestsResponse,
    status_code=http_status.HTTP_200_OK
)
async def get_approved_user(services: ServiceFactory = Depends(get_services)):
    """
    Получить список одобренных пользователей

    Требуемое состояние: ACTIVE

    Требуемые права доступа: GET_USER_TEST_RESULTS

    """
    return ApprovedRequestsResponse(content=await services.testing.get_approved_users())


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


@router.get(
    "/practical/{testing_id}/start",
    response_model=PracticalQuestionsResponse,
    status_code=http_status.HTTP_200_OK
)
async def start_practical_testing(testing_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Начать практическое тестирование по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: START_TESTING

    """
    return PracticalQuestionsResponse(
        content=await services.testing.start_practical_testing(testing_id)
    )


@router.get(
    "/theoretical/{testing_id}/start",
    response_model=TheoreticalQuestionsResponse,
    status_code=http_status.HTTP_200_OK
)
async def start_theoretical_testing(testing_id: UUID, services: ServiceFactory = Depends(get_services)):
    """
    Начать теоретическое тестирование по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: START_TESTING

    """
    return TheoreticalQuestionsResponse(
        content=await services.testing.start_theoretical_testing(testing_id)
    )


@router.post(
    "/practical/{testing_id}/finish",
    response_model=AttemptTestResponse,
    status_code=http_status.HTTP_200_OK
)
async def finish_practical_testing(
        testing_id: UUID,
        data: list[schemas.AnswerToPracticalQuestion],
        services: ServiceFactory = Depends(get_services)
):
    """
    Завершить практическое тестирование по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: COMPLETE_TESTING

    """
    return AttemptTestResponse(
        content=await services.testing.complete_practical_testing(testing_id, data)
    )


@router.post(
    "/theoretical/{testing_id}/finish",
    response_model=AttemptTestResponse,
    status_code=http_status.HTTP_200_OK
)
async def finish_theoretical_testing(
        testing_id: UUID,
        data: list[schemas.AnswerToTheoreticalQuestion],
        services: ServiceFactory = Depends(get_services)
):
    """
    Завершить теоретическое тестирование по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: COMPLETE_TESTING

    """
    return AttemptTestResponse(
        content=await services.testing.complete_theoretical_testing(testing_id, data)
    )


@router.post(
    "/{testing_id}/practical/new",
    response_model=PracticalQuestionResponse,
    status_code=http_status.HTTP_201_CREATED
)
async def new_practical_question(
        testing_id: UUID,
        data: schemas.PracticalQuestionCreate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Создать практический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_TESTING

    """
    return PracticalQuestionResponse(
        content=await services.testing.create_practical_question(testing_id, data)
    )


@router.post(
    "/{testing_id}/theoretical/new",
    response_model=TheoreticalQuestionResponse,
    status_code=http_status.HTTP_201_CREATED
)
async def new_theoretical_question(
        testing_id: UUID,
        data: schemas.TheoreticalQuestionCreate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Создать теоретический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_TESTING

    """
    return TheoreticalQuestionResponse(
        content=await services.testing.create_theoretical_question(testing_id, data)
    )


@router.get(
    "/practical/{question_id}",
    response_model=PracticalQuestionResponse,
    status_code=http_status.HTTP_200_OK
)
async def get_practical_question(
        question_id: UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить практический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    return PracticalQuestionResponse(
        content=await services.testing.get_practical_question(question_id)
    )


@router.get(
    "/theoretical/{question_id}",
    response_model=TheoreticalQuestionResponse,
    status_code=http_status.HTTP_200_OK
)
async def get_theoretical_question(
        question_id: UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить теоретический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    return TheoreticalQuestionResponse(
        content=await services.testing.get_theoretical_question(question_id)
    )


@router.post(
    "/practical/{question_id}",
    response_model=None,
    status_code=http_status.HTTP_204_NO_CONTENT
)
async def update_practical_question(
        question_id: UUID,
        data: schemas.PracticalQuestionUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить практический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    await services.testing.update_practical_question(question_id, data)


@router.post(
    "/theoretical/{question_id}",
    response_model=None,
    status_code=http_status.HTTP_204_NO_CONTENT
)
async def update_theoretical_question(
        question_id: UUID,
        data: schemas.TheoreticalQuestionUpdate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Обновить теоретический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    await services.testing.update_theoretical_question(question_id, data)


@router.delete(
    "/practical/{question_id}",
    response_model=None,
    status_code=http_status.HTTP_204_NO_CONTENT
)
async def delete_practical_question(
        question_id: UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Удалить практический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_TESTING

    """
    await services.testing.delete_practical_question(question_id)


@router.delete(
    "/theoretical/{question_id}",
    response_model=None,
    status_code=http_status.HTTP_204_NO_CONTENT
)
async def delete_theoretical_question(
        question_id: UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Удалить теоретический вопрос для тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: DELETE_TESTING

    """
    await services.testing.delete_theoretical_question(question_id)


@router.post(
    "/theoretical/{question_id}/option/new",
    response_model=TheoreticalQuestionResponse,
    status_code=http_status.HTTP_201_CREATED
)
async def create_theoretical_question_option(
        question_id: UUID,
        data: schemas.AnswerOptionCreate,
        services: ServiceFactory = Depends(get_services)
):
    """
    Создать вариант ответа для теоретического вопроса тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: CREATE_TESTING

    """
    return TheoreticalQuestionResponse(
        content=await services.testing.create_theoretical_question_option(question_id, data)
    )


@router.get(
    "/theoretical/{testing_id}/list",
    response_model=TheoreticalQuestionsResponse,
    status_code=http_status.HTTP_200_OK
)
async def get_theoretical_questions(
        testing_id: UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить вариант ответа для теоретического вопроса тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    return TheoreticalQuestionsResponse(
        content=await services.testing.get_theoretical_questions(testing_id)
    )


@router.get(
    "/practical/{testing_id}/list",
    response_model=PracticalQuestionsResponse,
    status_code=http_status.HTTP_200_OK
)
async def get_practical_questions(
        testing_id: UUID,
        services: ServiceFactory = Depends(get_services)
):
    """
    Получить вариант ответа для практического вопроса тестирования по id

    Требуемое состояние: ACTIVE

    Требуемые права доступа: UPDATE_TESTING

    """
    return PracticalQuestionsResponse(
        content=await services.testing.get_practical_questions(testing_id)
    )
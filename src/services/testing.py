import uuid
from datetime import datetime, timedelta
from typing import Literal

from src import exceptions
from src.models import schemas
from src.models.auth import BaseUser
from src.models.permission import Permission
from src.models.state import VacancyState, UserState, TestType
from src.services.auth.filters import permission_filter
from src.services.auth.filters import state_filter
from src.services.repository import AttemptRepo, VacancyRepo, PracticalQuestionRepo, TheoreticalQuestionRepo, \
    AnswerOptionRepo
from src.services.repository import TestingRepo


class TestingApplicationService:

    def __init__(
            self,
            current_user: BaseUser,
            testing_repo: TestingRepo,
            attempt_repo: AttemptRepo,
            vacancy_repo: VacancyRepo,
            practical_question_repo: PracticalQuestionRepo,
            theoretical_question_repo: TheoreticalQuestionRepo,
            answer_option_repo: AnswerOptionRepo
    ):
        self._current_user = current_user
        self._repo = testing_repo
        self._attempt_repo = attempt_repo
        self._vacancy_repo = vacancy_repo
        self._practical_question_repo = practical_question_repo
        self._theoretical_question_repo = theoretical_question_repo
        self._answer_option_repo = answer_option_repo

    @permission_filter(Permission.GET_SELF_TEST_RESULTS)
    @state_filter(UserState.ACTIVE)
    async def get_test_attempts(
            self,
            testing_id: uuid.UUID = None,
            page: int = 1,
            per_page: int = 10,
            order_by: Literal["title", "created_at"] = "created_at",
    ) -> list[schemas.AttemptTest]:
        """
        Получить список попыток прохождения теста текущего пользователя

        :param testing_id: id тестирования
        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1, но <= per_page_limit)
        :param order_by: поле сортировки
        :return:

        """

        if page < 1:
            raise exceptions.NotFound("Страница не найдена")
        if per_page < 1:
            raise exceptions.BadRequest("Неверное количество элементов на странице")

        per_page_limit = 40

        # Подготовка входных данных
        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        # Выполнение запроса
        attempts = await self._attempt_repo.get_all(
            limit=per_page,
            offset=offset,
            order_by=order_by,
            user_id=self._current_user.id,
            **{"test_id": testing_id}
        )
        return [schemas.AttemptTest.model_validate(attempt) for attempt in attempts]

    @permission_filter(Permission.GET_USER_TEST_RESULTS)
    @state_filter(UserState.ACTIVE)
    async def get_user_attempts(
            self,
            page: int = 1,
            per_page: int = 10,
            order_by: Literal["title", "created_at"] = "created_at",
            query: str = None,
            user_id: uuid.UUID = None
    ) -> list[schemas.AttemptTest]:
        """
        Получить общий список удачных попыток прохождения тестирования пользователей

        :param page: номер страницы (всегда >= 1)
        :param per_page: количество статей на странице (всегда >= 1, но <= per_page_limit)
        :param order_by: поле сортировки
        :param query: строка поиска
        :param user_id: id пользователя

        :return:

        """

        if page < 1:
            raise exceptions.NotFound("Страница не найдена")
        if per_page < 1:
            raise exceptions.BadRequest("Неверное количество элементов на странице")

        per_page_limit = 40

        # Подготовка входных данных
        per_page = min(per_page, per_page_limit, 2147483646)
        offset = min((page - 1) * per_page, 2147483646)

        # Выполнение запроса
        if query:
            attempts = await self._attempt_repo.search(
                limit=per_page,
                offset=offset,
                order_by=order_by,
                query=query,
                **{"user_id": user_id}
            )
        else:
            attempts = await self._attempt_repo.get_all(
                limit=per_page,
                offset=offset,
                order_by=order_by,
                **{"user_id": user_id}
            )
        return [schemas.AttemptTest.model_validate(attempt) for attempt in attempts]

    @permission_filter(Permission.START_TESTING)
    @state_filter(UserState.ACTIVE)
    async def start_practical_testing(self, testing_id: uuid.UUID) -> list[schemas.PracticalQuestion]:
        """
        Начать практическое тестирование

        :param testing_id: id тестирования
        :return:

        """
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        if testing.type != TestType.PRACTICAL:
            raise exceptions.BadRequest(f"Тестирование с id:{testing_id} не является практическим")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        first_attempt = await self._attempt_repo.get_first(
            user_id=self._current_user.id,
            test_id=testing_id
        )

        if first_attempt:
            time_now = datetime.now()
            time_deadline = first_attempt.created_at + timedelta(days=vacancy.test_time)

            if time_now > time_deadline:
                raise exceptions.BadRequest(f"Время прохождения теста истекло")

        questions = await self._practical_question_repo.get_all(testing_id=testing_id)
        return [schemas.PracticalQuestion.model_validate(question) for question in questions]

    @permission_filter(Permission.START_TESTING)
    @state_filter(UserState.ACTIVE)
    async def start_theoretical_testing(self, testing_id: uuid.UUID) -> list[schemas.TheoreticalQuestion]:
        """
        Начать теоретическое тестирование

        :param testing_id: id тестирования
        :return:

        """
        # Проверка наличия тестирования
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        if testing.type != TestType.THEORETICAL:
            raise exceptions.BadRequest(f"Тестирование с id:{testing_id} не является теоретическим")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        first_attempt = await self._attempt_repo.get_first(
            user_id=self._current_user.id,
            test_id=testing_id
        )

        if first_attempt:
            time_now = datetime.now()
            time_deadline = first_attempt.created_at + timedelta(days=vacancy.test_time)

            if time_now > time_deadline:
                raise exceptions.BadRequest(f"Время прохождения теста истекло")

        questions = await self._theoretical_question_repo.get_all(testing_id=testing_id, as_full=True)
        return [schemas.TheoreticalQuestion.model_validate(question) for question in questions]

    @permission_filter(Permission.COMPLETE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def complete_theoretical_testing(
            self,
            testing_id: uuid.UUID,
            answers: list[schemas.AnswerToTheoreticalQuestion]
    ) -> schemas.AttemptTest:
        """
        Завершить теоретическое тестирование

        :param testing_id: id тестирования
        :param answers: данные прохождения тестирования
        :return:

        """
        # Проверка наличия тестирования
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        if testing.type != TestType.THEORETICAL:
            raise exceptions.BadRequest(f"Тестирование с id:{testing_id} не является теоретическим")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        first_attempt = await self._attempt_repo.get_first(
            user_id=self._current_user.id,
            test_id=testing_id
        )

        if first_attempt:
            time_now = datetime.now().replace(tzinfo=None)
            time_deadline = (first_attempt.created_at + timedelta(days=vacancy.test_time)).replace(tzinfo=None)
            if time_now > time_deadline:
                raise exceptions.BadRequest(f"Время прохождения теста истекло")

        questions = await self._theoretical_question_repo.get_all(testing_id=testing_id, as_full=True)

        # Hashing
        questions_hash = {}
        for question in questions:
            option_hash = {}
            for option in question.answer_options:
                option_hash[option.id] = option
            questions_hash[question.id] = option_hash

        # Проверка ответов
        correct_answers = 0
        for answer in answers:
            options = questions_hash.get(answer.question_id)
            if options is None:
                raise exceptions.BadRequest(f"Вопрос с id:{answer.question_id} не найден")

            option = options.get(answer.answer_option_id)
            if option is None:
                raise exceptions.BadRequest(f"Вариант ответа с id:{answer.answer_option_id} не найден")

            if option.is_correct:
                correct_answers += 1

        all_questions = len(questions)

        if all_questions == 0:
            user_percent = 0
        else:
            user_percent = int((correct_answers * 100) / all_questions)

        attempt = schemas.AttemptTest.model_validate(
            await self._attempt_repo.create(
                percent=user_percent,
                user_id=self._current_user.id,
                test_id=testing_id,
            )
        )
        return schemas.AttemptTest(**attempt.model_dump(exclude={"test"}), test=schemas.Testing.model_validate(testing))

    @permission_filter(Permission.COMPLETE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def complete_practical_testing(
            self,
            testing_id: uuid.UUID,
            data: list[schemas.AnswerToPracticalQuestion]
    ) -> schemas.AttemptTest:
        """
        Завершить практическое тестирование

        :param testing_id: id тестирования
        :param data: данные прохождения тестирования
        :return:

        """
        # Проверка наличия тестирования
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        if testing.type != TestType.PRACTICAL:
            raise exceptions.BadRequest(f"Тестирование с id:{testing_id} не является практическим")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        first_attempt = await self._attempt_repo.get_first(
            user_id=self._current_user.id,
            test_id=testing_id
        )

        if first_attempt:
            time_now = datetime.now()
            time_deadline = first_attempt.created_at + timedelta(days=vacancy.test_time)

            if time_now > time_deadline:
                raise exceptions.BadRequest(f"Время прохождения теста истекло")

        questions = await self._practical_question_repo.get_all(testing_id=testing_id)
        correct_answers = 0

        # todo

        attempt = schemas.AttemptTest.model_validate(
            await self._attempt_repo.create(
                user_id=self._current_user.id,
                testing_id=testing_id,
                correct_answers=correct_answers,
                total_answers=len(questions)
            )
        )
        return schemas.AttemptTest(**attempt.model_dump(), test=schemas.Testing.model_validate(testing))

    @permission_filter(Permission.CREATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def create_testing(self, vacancy_id: uuid.UUID, data: schemas.TestingCreate) -> schemas.Testing:
        """
        Создать тестирование

        :param vacancy_id: id вакансии
        :param data: данные тестирования
        :return:

        """
        vacancy = await self._vacancy_repo.get(id=vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{vacancy_id} не открыта")

        testing = await self._repo.create(**data.model_dump(), vacancy_id=vacancy_id)
        return schemas.Testing.model_validate(testing)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def update_testing(self, testing_id: uuid.UUID, data: schemas.TestingUpdate) -> schemas.Testing:
        """
        Обновить тестирование

        :param testing_id: id тестирования
        :param data: данные тестирования
        :return:

        """
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        await self._repo.update(testing_id, **data.model_dump(exclude_unset=True))
        testing = await self._repo.get(id=testing_id)
        return schemas.Testing.model_validate(testing)

    @permission_filter(Permission.DELETE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def delete_testing(self, testing_id: uuid.UUID) -> None:
        """
        Удалить тестирование

        :param testing_id: id тестирования
        :return:

        """
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")
        # todo
        await self._repo.delete(id=testing_id)

    @permission_filter(Permission.GET_TESTING)
    @state_filter(UserState.ACTIVE)
    async def get_testing(self, testing_id: uuid.UUID) -> schemas.Testing:
        """
        Получить тестирование

        :param testing_id: id тестирования
        :return:

        """
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        return schemas.Testing.model_validate(testing)

    @permission_filter(Permission.GET_TESTING)
    @state_filter(UserState.ACTIVE)
    async def get_testings(self, vacancy_id: uuid.UUID, ) -> list[schemas.Testing]:
        """
        Получить список тестирований вакансии

        :param vacancy_id: id вакансии
        :return:

        """

        testings = await self._repo.get_all(vacancy_id=vacancy_id)
        return [schemas.Testing.model_validate(testing) for testing in testings]

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def create_practical_question(
            self,
            testing_id: uuid.UUID,
            data: schemas.PracticalQuestionCreate
    ) -> schemas.PracticalQuestion:
        """
        Создать практический вопрос для тестирования

        :param testing_id: id тестирования
        :param data: данные практического вопроса
        :return:

        """
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        if testing.type != TestType.PRACTICAL:
            raise exceptions.BadRequest(f"Тестирование с id:{testing_id} не является практическим")

        question = await self._practical_question_repo.create(**data.model_dump(), testing_id=testing_id)
        return schemas.PracticalQuestion.model_validate(question)

    @permission_filter(Permission.CREATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def create_theoretical_question(
            self,
            testing_id: uuid.UUID,
            data: schemas.TheoreticalQuestionCreate
    ) -> schemas.TheoreticalQuestion:
        """
        Создать теоретический вопрос для тестирования

        :param testing_id: id тестирования
        :param data: данные теоретического вопроса
        :return:

        """
        testing = await self._repo.get(id=testing_id)
        if not testing:
            raise exceptions.NotFound(f"Тестирование с id:{testing_id} не найдено")

        vacancy = await self._vacancy_repo.get(id=testing.vacancy_id)
        if not vacancy:
            raise exceptions.NotFound(f"Вакансия с id:{testing.vacancy_id} не найдена")

        if vacancy.state != VacancyState.OPENED:
            raise exceptions.BadRequest(f"Вакансия с id:{testing.vacancy_id} не открыта")

        if testing.type != TestType.THEORETICAL:
            raise exceptions.BadRequest(f"Тестирование с id:{testing_id} не является теоретическим")

        _ = await self._theoretical_question_repo.create(**data.model_dump(), testing_id=testing_id)
        question = await self._theoretical_question_repo.get(id=_.id, as_full=True)
        return schemas.TheoreticalQuestion.model_validate(question)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def update_practical_question(
            self,
            question_id: uuid.UUID,
            data: schemas.PracticalQuestionUpdate
    ) -> schemas.PracticalQuestion:
        """
        Обновить практический вопрос для тестирования

        :param question_id: id практического вопроса
        :param data: данные практического вопроса
        :return:

        """
        question = await self._practical_question_repo.get(id=question_id)
        if not question:
            raise exceptions.NotFound(f"Практический вопрос с id:{question_id} не найден")

        await self._practical_question_repo.update(question_id, **data.model_dump(exclude_unset=True))
        question = await self._practical_question_repo.get(id=question_id)
        return schemas.PracticalQuestion.model_validate(question)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def update_theoretical_question(
            self,
            question_id: uuid.UUID,
            data: schemas.TheoreticalQuestionUpdate
    ) -> schemas.TheoreticalQuestion:
        """
        Обновить теоретический вопрос для тестирования

        :param question_id: id теоретического вопроса
        :param data: данные теоретического вопроса
        :return:

        """
        question = await self._theoretical_question_repo.get(id=question_id)
        if not question:
            raise exceptions.NotFound(f"Теоретический вопрос с id:{question_id} не найден")

        await self._theoretical_question_repo.update(question_id, **data.model_dump(exclude_unset=True))
        question = await self._theoretical_question_repo.get(id=question_id)
        return schemas.TheoreticalQuestion.model_validate(question)

    @permission_filter(Permission.DELETE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def delete_practical_question(self, question_id: uuid.UUID) -> None:
        """
        Удалить практический вопрос для тестирования

        :param question_id: id практического вопроса
        :return:

        """
        question = await self._practical_question_repo.get(id=question_id)
        if not question:
            raise exceptions.NotFound(f"Практический вопрос с id:{question_id} не найден")

        await self._practical_question_repo.delete(id=question_id)

    @permission_filter(Permission.DELETE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def delete_theoretical_question(self, question_id: uuid.UUID) -> None:
        """
        Удалить теоретический вопрос для тестирования

        :param question_id: id теоретического вопроса
        :return:

        """
        question = await self._theoretical_question_repo.get(id=question_id)
        if not question:
            raise exceptions.NotFound(f"Теоретический вопрос с id:{question_id} не найден")

        await self._theoretical_question_repo.delete(id=question_id)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def get_practical_question(self, question_id: uuid.UUID) -> schemas.PracticalQuestion:
        """
        Получить практический вопрос для тестирования

        :param question_id: id практического вопроса
        :return:

        """
        question = await self._practical_question_repo.get(id=question_id)
        if not question:
            raise exceptions.NotFound(f"Практический вопрос с id:{question_id} не найден")

        return schemas.PracticalQuestion.model_validate(question)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def get_theoretical_question(self, question_id: uuid.UUID) -> schemas.TheoreticalQuestion:
        """
        Получить теоретический вопрос для тестирования

        :param question_id: id теоретического вопроса
        :return:

        """
        question = await self._theoretical_question_repo.get(id=question_id, as_full=True)
        if not question:
            raise exceptions.NotFound(f"Теоретический вопрос с id:{question_id} не найден")

        return schemas.TheoreticalQuestion.model_validate(question)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def create_theoretical_question_option(
            self,
            question_id: uuid.UUID,
            data: schemas.AnswerOptionCreate
    ) -> schemas.TheoreticalQuestion:
        """
        Создать вариант ответа на теоретический вопрос

        :param question_id: id теоретического вопроса
        :param data: данные варианта ответа
        :return:

        """
        question = await self._theoretical_question_repo.get(id=question_id)
        if not question:
            raise exceptions.NotFound(f"Теоретический вопрос с id:{question_id} не найден")

        await self._answer_option_repo.create(**data.model_dump(), question_id=question_id)
        new_question = await self._theoretical_question_repo.get(id=question.id, as_full=True)
        return schemas.TheoreticalQuestion.model_validate(new_question)

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def get_practical_questions(self, testing_id: uuid.UUID) -> list[schemas.PracticalQuestion]:
        """
        Получить список практических вопросов для тестирования

        :param testing_id: id тестирования
        :return:

        """
        questions = await self._practical_question_repo.get_all(testing_id=testing_id)
        return [schemas.PracticalQuestion.model_validate(question) for question in questions]

    @permission_filter(Permission.UPDATE_TESTING)
    @state_filter(UserState.ACTIVE)
    async def get_theoretical_questions(self, testing_id: uuid.UUID) -> list[schemas.TheoreticalQuestion]:
        """
        Получить список теоретических вопросов для тестирования

        :param testing_id: id тестирования
        :return:

        """
        questions = await self._theoretical_question_repo.get_all(testing_id=testing_id, as_full=True)
        return [schemas.TheoreticalQuestion.model_validate(question) for question in questions]

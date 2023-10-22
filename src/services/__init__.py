from src.models.auth import BaseUser
from . import auth
from . import repository
from .testing import TestingApplicationService
from .vacancy import VacancyApplicationService
from .permission import PermissionApplicationService
from .stats import StatsApplicationService


class ServiceFactory:
    def __init__(
            self,
            repo_factory: repository.RepoFactory,
            *,
            current_user: BaseUser,
            config,
            file_storage,
            http_client,
            db_lazy_session,
    ):
        self._repo = repo_factory
        self._current_user = current_user
        self._config = config
        self._file_storage = file_storage
        self._http_client = http_client
        self._db_lazy_session = db_lazy_session

    @property
    def vacancy(self) -> VacancyApplicationService:
        return VacancyApplicationService(
            self._current_user,
            vacancy_repo=self._repo.vacancy,
            file_repo=self._repo.file,
            file_storage=self._file_storage,
        )

    @property
    def testing(self) -> TestingApplicationService:
        return TestingApplicationService(
            self._current_user,
            testing_repo=self._repo.testing,
            attempt_repo=self._repo.attempt,
            vacancy_repo=self._repo.vacancy,
            practical_question_repo=self._repo.practical_question,
            theoretical_question_repo=self._repo.theoretical_question,
            answer_option_repo=self._repo.answer_option,
            http_client=self._http_client,
            config=self._config,
            db_lazy_session=self._db_lazy_session,
        )

    @property
    def stats(self) -> StatsApplicationService:
        return StatsApplicationService(config=self._config)

    @property
    def permission(self) -> PermissionApplicationService:
        return PermissionApplicationService()

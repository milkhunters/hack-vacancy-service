from .file import FileRepo
from .vacancy import VacancyRepo
from .testing import TestingRepo
from .attempt import AttemptRepo
from .theoretical_question import TheoreticalQuestionRepo
from .practical_question import PracticalQuestionRepo
from .answer_option import AnswerOptionRepo


class RepoFactory:
    def __init__(self, session):
        self._session = session

    @property
    def vacancy(self) -> VacancyRepo:
        return VacancyRepo(self._session)

    @property
    def file(self) -> FileRepo:
        return FileRepo(self._session)

    @property
    def testing(self) -> TestingRepo:
        return TestingRepo(self._session)

    @property
    def attempt(self) -> AttemptRepo:
        return AttemptRepo(self._session)

    @property
    def theoretical_question(self) -> TheoreticalQuestionRepo:
        return TheoreticalQuestionRepo(self._session)

    @property
    def practical_question(self) -> PracticalQuestionRepo:
        return PracticalQuestionRepo(self._session)

    @property
    def answer_option(self) -> AnswerOptionRepo:
        return AnswerOptionRepo(self._session)

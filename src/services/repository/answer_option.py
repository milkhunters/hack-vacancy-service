from src.models import tables
from src.services.repository.base import BaseRepository


class AnswerOptionRepo(BaseRepository[tables.AnswerOption]):
    table = tables.AnswerOption

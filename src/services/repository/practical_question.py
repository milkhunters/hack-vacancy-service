from src.models import tables
from src.services.repository.base import BaseRepository


class PracticalQuestionRepo(BaseRepository[tables.PracticalQuestion]):
    table = tables.PracticalQuestion

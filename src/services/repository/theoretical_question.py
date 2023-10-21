from src.models import tables
from src.services.repository.base import BaseRepository


class TheoreticalQuestionRepo(BaseRepository[tables.TheoreticalQuestion]):
    table = tables.TheoreticalQuestion

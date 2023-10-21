from src.models import tables
from src.services.repository.base import BaseRepository


class TestingRepo(BaseRepository[tables.Testing]):
    table = tables.Testing

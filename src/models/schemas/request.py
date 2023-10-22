from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from src.models.state import VacancyState, VacancyType


class ApprovedRequests(BaseModel):
    user_id: UUID
    vacancy_id: UUID
    vacancy_title: str
    vacancy_state: VacancyState
    vacancy_type: VacancyType
    vacancy_created_at: datetime
    testings: list[dict[str, str | UUID | int]]


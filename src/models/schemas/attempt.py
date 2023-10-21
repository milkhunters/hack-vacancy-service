from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from src.models.schemas import Testing


class Attempt(BaseModel):
    id: UUID
    percent: int
    user_id: UUID
    test_id: UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class AttemptTest(Attempt):
    test: Testing

    class Config:
        from_attributes = True

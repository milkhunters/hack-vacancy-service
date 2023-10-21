from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, validator, field_validator

from src.models.state import TestType


class Testing(BaseModel):
    id: UUID
    title: str
    content: str
    type: TestType
    correct_percent: int

    vacancy_id: UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class TestingCreate(BaseModel):
    title: str
    content: str
    type: TestType
    correct_percent: int

    @field_validator('title')
    def validate_title(cls, v):
        if len(v) > 255:
            raise ValueError('Название теста должно быть не более 255 символов')
        return v

    @field_validator('content')
    def validate_content(cls, v):
        if len(v) > 32000:
            raise ValueError('Описание теста должно быть не более 32000 символов')
        return v

    @field_validator('correct_percent')
    def validate_correct_percent(cls, v):
        if v < 0 or v > 100:
            raise ValueError('Проходной процент должен быть в диапазоне от 0 до 100')
        return v


class TestingUpdate(BaseModel):
    title: str = None
    content: str = None
    type: TestType = None
    correct_percent: int = None

    @field_validator('title')
    def validate_title(cls, v):
        if v and len(v) > 255:
            raise ValueError('Название теста должно быть не более 255 символов')
        return v

    @field_validator('content')
    def validate_content(cls, v):
        if v and len(v) > 32000:
            raise ValueError('Описание теста должно быть не более 32000 символов')
        return v

    @field_validator('correct_percent')
    def validate_correct_percent(cls, v):
        if v and (v < 0 or v > 100):
            raise ValueError('Проходной процент должен быть в диапазоне от 0 до 100')
        return v



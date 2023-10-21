from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator

from src.models.language import ProgramLanguage


class PracticalQuestion(BaseModel):
    id: UUID
    content: str
    language: ProgramLanguage
    answer: str

    testing_id: UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class PracticalQuestionCreate(BaseModel):
    content: str
    language: ProgramLanguage
    answer: str

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if len(value) > 32000:
            raise ValueError("Содержание не может быть более 32000 символов")
        return value

    @field_validator('answer')
    def answer_must_be_valid(cls, value):
        if len(value) > 255:
            raise ValueError("Ответ не может быть более 32000 символов")
        return value


class PracticalQuestionUpdate(BaseModel):
    content: str = None
    language: ProgramLanguage = None
    answer: str = None

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if value and len(value) > 32000:
            raise ValueError("Содержание не может быть более 32000 символов")
        return value

    @field_validator('answer')
    def answer_must_be_valid(cls, value):
        if value and len(value) > 255:
            raise ValueError("Ответ не может быть более 32000 символов")
        return value


class AnswerOption(BaseModel):
    id: UUID
    content: str
    is_correct: bool

    question_id: UUID

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class TheoreticalQuestion(BaseModel):
    id: UUID
    content: str

    testing_id: UUID
    answer_options: list[AnswerOption]

    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True


class TheoreticalQuestionCreate(BaseModel):
    content: str

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if len(value) > 32000:
            raise ValueError("Содержание не может быть более 32000 символов")
        return value


class TheoreticalQuestionUpdate(BaseModel):
    content: str = None

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if value and len(value) > 32000:
            raise ValueError("Содержание не может быть более 32000 символов")
        return value


class AnswerOptionCreate(BaseModel):
    content: str
    is_correct: bool

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if len(value) > 32000:
            raise ValueError("Содержание не может быть более 32000 символов")
        return value


class AnswerOptionUpdate(BaseModel):
    content: str = None
    is_correct: bool = None

    @field_validator('content')
    def content_must_be_valid(cls, value):
        if value and len(value) > 32000:
            raise ValueError("Содержание не может быть более 32000 символов")
        return value


class AnswerToTheoreticalQuestion(BaseModel):
    answer_option_id: UUID
    question_id: UUID
    attempt_id: UUID


class AnswerToPracticalQuestion(BaseModel):
    answer: str
    question_id: UUID
    attempt_id: UUID

from .base import BaseView
from src.models import schemas


class TestingsResponse(BaseView):
    content: list[schemas.Testing]


class TestingResponse(BaseView):
    content: schemas.Testing


class AttemptTestResponse(BaseView):
    content: schemas.AttemptTest


class AttemptsTestResponse(BaseView):
    content: list[schemas.AttemptTest]


class PracticalQuestionResponse(BaseView):
    content: schemas.PracticalQuestion


class PracticalQuestionsResponse(BaseView):
    content: list[schemas.PracticalQuestion]


class TheoreticalQuestionResponse(BaseView):
    content: schemas.TheoreticalQuestion


class TheoreticalQuestionsResponse(BaseView):
    content: list[schemas.TheoreticalQuestion]


class ProgramResultResponse(BaseView):
    content: schemas.ProgramResult

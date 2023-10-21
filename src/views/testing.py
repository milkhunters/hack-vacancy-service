from .base import BaseView
from src.models import schemas


class TestingsResponse(BaseView):
    content: list[schemas.Testing]


class TestingResponse(BaseView):
    content: schemas.Testing


class AttemptsTestResponse(BaseView):
    content: list[schemas.AttemptTest]

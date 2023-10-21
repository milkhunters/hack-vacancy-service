from .base import BaseView
from src.models import schemas


class VacancyResponse(BaseView):
    content: schemas.Vacancy


class VacanciesResponse(BaseView):
    content: list[schemas.VacancySmall]


class VacancyFilesResponse(BaseView):
    content: list[schemas.VacancyFileItem]


class VacancyFileResponse(BaseView):
    content: schemas.VacancyFileItem


class VacancyFileUploadResponse(BaseView):
    content: schemas.VacancyFileUpload

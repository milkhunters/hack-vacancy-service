from .base import BaseView
from src.models import schemas


class ApprovedRequestsResponse(BaseView):
    content: list[schemas.ApprovedRequests]

import uuid

from sqlalchemy import Column, UUID, VARCHAR, Enum, DateTime, func, INTEGER
from sqlalchemy.orm import relationship

from src.db import Base

from src.models.state import VacancyState, VacancyType


class Vacancy(Base):
    """
    The Vacancy model
    """
    __tablename__ = "vacancies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(255), nullable=False)
    poster = Column(UUID(as_uuid=True), nullable=True)
    content = Column(VARCHAR(32000), nullable=False)
    type = Column(Enum(VacancyType), default=VacancyType.INTERNSHIP, nullable=False)
    state = Column(Enum(VacancyState), default=VacancyState.CLOSED, nullable=False)
    test_time = Column(INTEGER(), nullable=False)

    files = relationship("models.tables.file.File", back_populates="vacancy")
    testing = relationship("models.tables.testing.Testing", back_populates="vacancy")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

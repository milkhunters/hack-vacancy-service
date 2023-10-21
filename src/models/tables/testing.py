import uuid

from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, VARCHAR, Enum, INTEGER
from sqlalchemy.orm import relationship

from src.db import Base
from src.models.state import TestType


class Testing(Base):
    """
    The Testing model

    """
    __tablename__ = "testing"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(VARCHAR(255), nullable=False)
    content = Column(VARCHAR(32000), nullable=False)
    type = Column(Enum(TestType), nullable=False)
    correct_percent = Column(INTEGER, nullable=False)

    vacancy_id = Column(UUID(as_uuid=True), ForeignKey("vacancies.id"), nullable=False)
    vacancy = relationship("models.tables.vacancy.Vacancy", back_populates="testing")
    attempts = relationship("models.tables.attempt.Attempt", back_populates="test")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

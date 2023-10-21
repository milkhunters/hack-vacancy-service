import uuid

from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, VARCHAR, Enum
from sqlalchemy.orm import relationship

from src.db import Base
from src.models.language import ProgramLanguage


class PracticalQuestion(Base):
    """
    The PracticalQuestion model

    """
    __tablename__ = "practical_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(VARCHAR(32000), nullable=False)
    language = Column(Enum(ProgramLanguage), nullable=False)
    answer = Column(VARCHAR(255), nullable=False)

    testing_id = Column(UUID(as_uuid=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

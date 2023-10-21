import uuid

from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, VARCHAR, BOOLEAN
from sqlalchemy.orm import relationship

from src.db import Base


class TheoreticalQuestion(Base):
    """
    The TheoreticalQuestion model

    """
    __tablename__ = "theoretical_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(VARCHAR(32000), nullable=False)

    testing_id = Column(UUID(as_uuid=True), nullable=False)
    answer_options = relationship("models.tables.theoretical_question.AnswerOption", back_populates="question")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'


class AnswerOption(Base):
    """
    The AnswerOptions model

    """
    __tablename__ = "answer_options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(VARCHAR(320), nullable=False)
    is_correct = Column(BOOLEAN, default=False)

    question_id = Column(UUID(as_uuid=True), ForeignKey("theoretical_questions.id"), nullable=False)
    question = relationship("models.tables.theoretical_question.TheoreticalQuestion", back_populates="answer_options")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

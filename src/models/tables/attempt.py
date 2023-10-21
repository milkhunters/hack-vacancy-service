import uuid

from sqlalchemy import Column, UUID, DateTime, func, ForeignKey, INTEGER
from sqlalchemy.orm import relationship

from src.db import Base


class Attempt(Base):
    """
    The Attempt model

    """
    __tablename__ = "attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    percent = Column(INTEGER, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)

    test_id = Column(UUID(as_uuid=True), ForeignKey("testing.id"), nullable=False)
    test = relationship("models.tables.testing.Testing", back_populates="attempts")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.id}>'

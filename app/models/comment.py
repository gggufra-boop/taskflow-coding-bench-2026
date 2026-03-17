"""Comment model for task discussions."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, task_id={self.task_id}, author_id={self.author_id})>"

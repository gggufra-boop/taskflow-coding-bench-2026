"""Workflow model for configurable task status transitions."""

import json
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    definition = Column(Text, nullable=False)  # JSON string for SQLite compatibility
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="workflow")

    def get_definition_dict(self) -> dict:
        """Parse the JSON definition string into a dictionary."""
        return json.loads(self.definition)

    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}')>"

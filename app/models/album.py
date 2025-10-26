import uuid
from typing import List

from sqlalchemy import String, Text, Boolean, JSON
from sqlalchemy.orm import Mapped

from app.db import Base
from app.utils.mixins import TimestampMixin
from app.models.base import mapped_column


class Album(TimestampMixin, Base):
    __tablename__ = 'album'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    name: Mapped[str] = mapped_column(String)
    is_ai_generated: Mapped[bool] = mapped_column(Boolean)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    theme: Mapped[str] = mapped_column(String, nullable=True)  # For AI-generated albums
    photo_ids: Mapped[List[str]] = mapped_column(JSON, nullable=True)  # List of photo IDs in the album

    def __repr__(self):
        return f"<Album(id={self.id}, name={self.name})>"


import uuid
from datetime import datetime
from typing import List

from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, relationship

from app.db import Base
from app.utils.mixins import TimestampMixin
from app.models.base import mapped_column


class Photo(TimestampMixin, Base):
    __tablename__ = 'photo'

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    filename: Mapped[str] = mapped_column(String)
    original_filename: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String)
    # upload_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    width: Mapped[int] = mapped_column(Integer, nullable=True)
    height: Mapped[int] = mapped_column(Integer, nullable=True)

    # AI Analysis results
    caption: Mapped[str] = mapped_column(Text, nullable=True)
    tags: Mapped[List[str]] = mapped_column(JSON, nullable=True)  # List of tags
    embedding: Mapped[List[int]] = mapped_column(JSON, nullable=True)  # Embedding vector
    analysis_status: Mapped[str] = mapped_column(String, default='pending')  # pending, processing, completed, failed
    analysis_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationships - TODO: Uncomment when EmotionAnalysis and ColorAnalysis models are created
    # emotion_analysis = relationship('EmotionAnalysis', back_populates='photo', uselist=False)
    # color_analysis = relationship('ColorAnalysis', back_populates='photo', uselist=False)

    def __repr__(self):
        return f'<Photo(id={self.id}, filename={self.filename})>'


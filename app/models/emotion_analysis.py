from typing import List

from sqlalchemy import Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, relationship

from app.db import Base
from app.models.base import mapped_column


class EmotionAnalysis(Base):
    __tablename__ = 'emotion_analysis'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    photo_id: Mapped[str] = mapped_column(String, ForeignKey('photo.id'), nullable=False)

    emotions: Mapped[List[str]] = mapped_column(JSON)  # Dictionary of emotions and confidence scores

    dominant_emotion: Mapped[str] = mapped_column(String)
    confidence_score: Mapped[float] = mapped_column(Float)
    # analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    photo = relationship('Photo', back_populates='emotion_analysis')

    def __repr__(self):
        return f'<EmotionAnalysis(photo_id={self.photo_id}, dominant_emotion={self.dominant_emotion})>'


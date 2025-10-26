from datetime import datetime
from typing import List

from sqlalchemy import Integer, Text, DateTime, JSON
from sqlalchemy.orm import Mapped

from app.db import Base
from app.models.base import mapped_column


class DailySummary(Base):
    __tablename__ = 'daily_summaries'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    photo_count: Mapped[int] = mapped_column(Integer, default=0)
    
    dominant_emotions: Mapped[List[str]] = mapped_column(JSON)
    dominant_colors: Mapped[List[str]] = mapped_column(JSON)
    themes: Mapped[List[str]] = mapped_column(JSON)  # AI-generated themes for the day
    
    summary_text: Mapped[str] = mapped_column(Text)  # AI-generated summary
    # created_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DailySummary(date={self.date}, photo_count={self.photo_count})>'


from typing import List

from sqlalchemy import Integer, String, ForeignKey, Float, JSON
from sqlalchemy.orm import Mapped, relationship

from app.db import Base
from app.utils.mixins import TimestampMixin
from app.models.base import mapped_column


class ColorAnalysis(TimestampMixin, Base):
    __tablename__ = 'color_analysis'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    photo_id: Mapped[str] = mapped_column(String, ForeignKey('photo.id'), nullable=False)

    dominant_colors: Mapped[List[str]] = mapped_column(JSON)  # List of dominant colors with hex codes
    color_palette: Mapped[List[str]] = mapped_column(JSON)  # Extended color palette

    brightness: Mapped[float] = mapped_column(Float)  # Overall brightness score
    saturation: Mapped[float] = mapped_column(Float)  # Overall saturation score
    # analysis_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationship
    photo = relationship('Photo', back_populates='color_analysis')

    def __repr__(self):
        return f'<ColorAnalysis(photo_id={self.photo_id})>'


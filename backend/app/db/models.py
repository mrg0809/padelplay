from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.connection import Base

class Court(Base):
    __tablename__ = "courts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    club_id = Column(UUID(as_uuid=True), ForeignKey("clubs.id"), nullable=False)
    price_per_hour = Column(DECIMAL(10, 2), nullable=False)
    price_per_hour_and_half = Column(DECIMAL(10, 2))
    is_active = Column(Boolean, default=True)

    # Relaciones
    club = relationship("Club", back_populates="courts")

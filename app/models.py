from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base

def utc_now() -> datetime:
    """ Current time in UTC. """
    return datetime.now(timezone.utc)


class Address(Base):
    """ Address model. """
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str | None] = mapped_column(String(100))
    street: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(100))
    country: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
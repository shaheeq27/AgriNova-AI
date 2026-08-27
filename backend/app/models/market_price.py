"""
AgriNova AI — MarketPrice model (V5.1).

Stores market commodity prices fetched from external data sources.
Each row represents one commodity's price at one market on one date.
"""

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Float, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MarketPrice(Base):
    """A single market price record for a commodity at a mandi."""

    __tablename__ = "market_prices"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    commodity: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    variety: Mapped[str | None] = mapped_column(String(100), nullable=True)
    market_name: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    district: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    modal_price: Mapped[float] = mapped_column(Float, nullable=False)
    price_date: Mapped[date] = mapped_column(Date, nullable=False)
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, default="demo"
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Composite index for the most common query pattern
    __table_args__ = (
        Index(
            "ix_market_prices_commodity_state_date",
            "commodity",
            "state",
            "price_date",
        ),
        Index(
            "ix_market_prices_market_date",
            "market_name",
            "price_date",
        ),
    )

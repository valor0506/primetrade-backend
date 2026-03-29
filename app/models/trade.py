from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, func

from app.db.base import Base


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    symbol = Column(String(20), nullable=False, index=True)
    trade_type = Column(Enum("buy", "sell", name="trade_type"), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(
        Enum("open", "closed", "cancelled", name="trade_status"),
        default="open",
        nullable=False,
    )
    notes = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
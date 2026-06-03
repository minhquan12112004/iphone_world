from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

from sqlalchemy.dialects.postgresql import UUID

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True, nullable=False)
    order_number = Column(String, unique=True, index=True, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="PENDING", index=True) # PENDING, SYNCED, FAILED
    odoo_order_id = Column(Integer, nullable=True) # ID in Odoo
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False) # Snapshot of price at time of order

    order = relationship("Order", back_populates="items")
    product = relationship("Product")

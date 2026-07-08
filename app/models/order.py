from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    ordered = "ordered"
    shipped = "shipped"
    delivered = "delivered"

    @property
    def priority(self):
        return {
            OrderStatus.pending: 0,
            OrderStatus.ordered: 1,
            OrderStatus.shipped: 2,
            OrderStatus.delivered: 3,
        }[self]

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus))

    

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus))

    def __repr__(self):
        return f"ID:{self.id}, ORDERED BY:{self.customer_id}"
    
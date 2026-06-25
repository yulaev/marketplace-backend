from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
import enum

class OrderStatus(str, enum.Enum):
    pending = "pending"
    ordered = "ordered"
    shipped = "shipped"
    delivered = "delivered"

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

    def __repr__(self):
        return f"ID:{self.id}, DATE:{self.order_date}, ORDERED BY:{self.customer_id}"
    
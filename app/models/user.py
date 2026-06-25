from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column
import enum
from .base import Base

class UserRole(str, enum.Enum):
    customer = "customer"
    seller = "seller"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(60))
    email: Mapped[str] = mapped_column(String(50), unique=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole))

    def __repr__(self):
        return f"ID:{self.id}, NAME:{self.name}, EMAIL:{self.email}, ROLE:{self.role}"

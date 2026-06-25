from pydantic import BaseModel, Field
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: Decimal = Field(ge=0)
    quantity: int = Field(default=1, ge=1)

class ProductEdit(BaseModel):
    name: str | None = None
    description: str | None = None
    price: Decimal = Field(default=None, gt=0)
    quantity: int = Field(default=None, ge=1)
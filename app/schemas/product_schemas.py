from pydantic import BaseModel, Field
from decimal import Decimal

class ProductCreate(BaseModel):
    name: str = Field(min_length=2)
    description: str | None = None
    price: Decimal = Field(ge=0)
    quantity: int = Field(default=1, ge=1)

class ProductEdit(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    description: str | None = Field(default=None, min_length=0)
    price: Decimal | None = Field(default=None, gt=0)

class ProductRestock(BaseModel):
    quantity: int = Field(default=None)
from pydantic import BaseModel, Field

class AddToCartBody(BaseModel):
    id: int
    quantity: int = Field(ge=1)
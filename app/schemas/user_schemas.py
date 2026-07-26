from pydantic import BaseModel, EmailStr, Field
from app.models import UserRole

class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    password: str = Field(min_length=4)
    email: EmailStr
    role: UserRole = UserRole.customer

class UserPublic(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: UserRole

# class UserPrivate(UserPublic):
#     password_hash: str

class UserEdit(BaseModel):
    id: int
    name: str | None = None
    email: str | None = None
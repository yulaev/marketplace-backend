from pydantic import BaseModel
from models import UserRole

class UserModel(BaseModel):
    name: str
    password: str
    email: str
    role: UserRole.customer

class SignInModel(BaseModel):
    name: str
    password: str

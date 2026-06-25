from app.database import get_session
from app.schemas import UserCreate, UserEdit, UserPublic
from app.models import User, UserRole
from app.utilities import oauth2_scheme, get_access_token, authenticate_user, validate_token
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
import bcrypt
from typing import Annotated
from sqlalchemy import select


def sign_up(data: UserCreate):
    with get_session() as session:
        if data.role == UserRole.admin:
            raise HTTPException(status_code=403, detail="You are Forbidden from performing this operation")

        s = bcrypt.gensalt()
        pw = data.password.encode("utf-8")
        pw_hash = bcrypt.hashpw(pw, s)
        pw_db = pw_hash.decode("utf-8")
        
        user = User(
            name = data.name,
            password_hash = pw_db,
            email = data.email,
            role = data.role
        )

        session.add(user)
        session.commit()
    
def sing_in(data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    with get_session() as session:
        stmt = select(User).where(User.name == data.username)
        user = session.scalar(stmt)
        if not authenticate_user(data, user):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        token = get_access_token(user)
        return token
    
def edit_user(token: Annotated[str, Depends(oauth2_scheme)], edit_body: UserEdit, id: int):
    with get_session() as session:
        payload = validate_token(token)
        user = session.get(User, id)
        if payload.get("sub") != user.name:
            raise HTTPException(status_code=403, detail="You are forbidden from performing this operation")
        
        edit_user = edit_body.model_dump(exclude_unset=True)
        for key, value, in edit_user.items():
            setattr(user, key, value)

        session.commit()

def delete_user(token: Annotated[str, Depends(oauth2_scheme)], id: int):
    with get_session() as session:
        payload = validate_token(token)
        user = session.get(User, id)
        if payload.get("sub") != user.name:
            raise HTTPException(status_code=403, detail="You are forbidden from performing this operation")
        
        session.delete(user)
        session.commit()

def get_user(id: int):
    with get_session() as session:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_display = UserPublic(
            id = user.id,
            name = user.name,
            email = user.email,
            role = user.role
        )
    return user_display
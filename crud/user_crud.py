from database import get_session
from schemas import UserModel, SignInModel
from models import User, UserRole
from fastapi import HTTPException
from sqlalchemy import select
import bcrypt


def sign_up(data: UserModel):
    with get_session() as session:
        if data.role == UserRole.admin:
            raise HTTPException(status_code=403)

        s = bcrypt.gensalt()
        pw = data.password.encode("utf-8")
        pw_hash = bcrypt.hashpw(pw, s)
        
        user = User(
            name = data.name,
            password_hash = pw_hash,
            email = data.email,
            role = data.role
        )

        session.add(user)
        session.commit()

        return user
    
def sing_in(data: SignInModel):
    with get_session() as session:
        user = session.get(User, data.name)
        if bcrypt.checkpw(data.password, user.password_hash):
            return True
        else:
            return False
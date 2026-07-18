from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from typing import Annotated
from sqlalchemy.orm import Session

from app.crud import sign_up, sing_in, edit_user, delete_user, get_user
from app.schemas import UserCreate, UserEdit
from app.utilities import oauth2_scheme
from app.database import get_session
 
router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/sign-up")
async def sign_up_r(data: UserCreate, session: Annotated[Session, Depends(get_session)]):
    sign_up(data, session)
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@router.post("/sign-in")
async def sign_in_r(data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Annotated[Session, Depends(get_session)]):
    token = sing_in(data, session)
    return token

@router.patch("/edit-user")
async def edit_user_r(token: Annotated[str, Depends(oauth2_scheme)], edit_body: UserEdit, session: Annotated[Session, Depends(get_session)]):
    edit_user(token, edit_body, session)
    return JSONResponse(status_code=200, content={"message": "User edited successfully"})

@router.delete("/delete-user")
async def delete_user_r(token: Annotated[str, Depends(oauth2_scheme)], id: int,  session: Annotated[Session, Depends(get_session)]):
    delete_user(token, id, session)
    return JSONResponse(status_code=200, content={"message": "User deleted successfully"})

@router.get("/{id}")
def get_user_r(id: int, session: Annotated[Session, Depends(get_session)]):
    user = get_user(id, session)
    return user
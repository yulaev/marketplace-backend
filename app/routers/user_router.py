from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from app.crud import sign_up, sing_in, edit_user, delete_user, get_user
from app.schemas import UserCreate, UserEdit
from typing import Annotated
from app.utilities import oauth2_scheme

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/sign-up")
async def sign_up_r(data: UserCreate):
    sign_up(data)
    return JSONResponse(status_code=201, content={"message": "User created successfully"})

@router.post("/sign-in")
async def sign_in_r(data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    token = sing_in(data)
    return token

@router.patch("/edit-user")
async def edit_user_r(token: Annotated[str, Depends(oauth2_scheme)], edit_body: UserEdit, id: int):
    edit_user(token, edit_body, id)
    return JSONResponse(status_code=200, content={"message": "User edited successfully"})

@router.delete("/delete-user")
async def delete_user_r(token: Annotated[str, Depends(oauth2_scheme)], id: int):
    delete_user(token, id)
    return JSONResponse(status_code=200, content={"message": "User deleted succesfully"})

@router.get("/{id}")
def get_user_r(id: int):
    user = get_user(id)
    return user
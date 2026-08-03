from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Annotated
from sqlalchemy.orm import Session
from app.database import get_session

from app.crud import create_product, edit_product, restock_product, delete_product, get_product
from app.schemas import ProductCreate, ProductEdit, ProductRestock
from app.utilities import oauth2_scheme

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/create-product")
async def create_product_r(data: ProductCreate, token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
    create_product(data, token, session)
    return JSONResponse(status_code=201, content={"message": "Product succesfully listed"})

@router.patch("/edit-product")
async def edit_product_r(token: Annotated[str, Depends(oauth2_scheme)], edit_body: ProductEdit, id: int, session: Annotated[Session, Depends(get_session)]):
    edit_product(token, edit_body, id, session)
    return JSONResponse(status_code=200, content={"message": "Listing succesfully edited"})

@router.patch("/restock-product")
async def edit_product_r(token: Annotated[str, Depends(oauth2_scheme)], restock_body: ProductRestock, id: int, session: Annotated[Session, Depends(get_session)]):
    restock_product(token, restock_body, id, session)
    return JSONResponse(status_code=200, content={"message": "Product succesfully restocked"})

@router.delete("/delete-listing")
async def delete_product_r(token: Annotated[str, Depends(oauth2_scheme)], id: int, session: Annotated[Session, Depends(get_session)]):
    delete_product(token, id, session)
    return JSONResponse(status_code=200, content={"message": "Listing deleted succesfully"})

@router.get("/{id}")
async def get_product_r(id: int, session: Annotated[Session, Depends(get_session)]):
    product = get_product(id, session)
    return product
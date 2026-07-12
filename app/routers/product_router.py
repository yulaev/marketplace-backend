from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.crud import list_product, edit_product, restock_product, delete_product, get_product
from app.schemas import ProductCreate, ProductEdit, ProductRestock
from typing import Annotated
from app.utilities import oauth2_scheme

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/list-a-product")
async def list_product_r(data: ProductCreate, token: Annotated[str, Depends(oauth2_scheme)]):
    list_product(data, token)
    return JSONResponse(status_code=201, content={"message": "Product succesfully listed"})

@router.patch("/edit-listing")
async def edit_product_r(token: Annotated[str, Depends(oauth2_scheme)], edit_body: ProductEdit, id: int):
    edit_product(token, edit_body, id)
    return JSONResponse(status_code=200, content={"message": "Listing succesfully edited"})

@router.patch("/restock-product")
async def edit_product_r(token: Annotated[str, Depends(oauth2_scheme)], restock_body: ProductRestock, id: int):
    restock_product(token, restock_body, id)
    return JSONResponse(status_code=200, content={"message": "Product succesfully restocked"})

@router.delete("/delete-listing")
async def delete_product_r(token: Annotated[str, Depends(oauth2_scheme)], id: int):
    delete_product(token, id)
    return JSONResponse(status_code=200, content={"message": "Listing deleted succesfully"})

@router.get("/{id}")
async def get_product_r(id: int):
    product = get_product(id)
    return product
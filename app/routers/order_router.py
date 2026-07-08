from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from app.crud import add_to_cart, remove_from_cart, get_cart, place_order
from app.schemas import AddToCartBody, PublicOrder
from typing import Annotated
from app.utilities import oauth2_scheme

router = APIRouter(
    prefix="/order",
    tags=["order"]
)

@router.post("/add-to-cart")
async def add_to_cart_r(token: Annotated[str, Depends(oauth2_scheme)], item_data: AddToCartBody):
    add_to_cart(token, item_data)
    return JSONResponse(status_code=201, content={"message": "Succesfully added to cart"})

@router.delete("/remove-from-cart")
async def remove_from_cart_r(token: Annotated[str, Depends(oauth2_scheme)], id: int):
    remove_from_cart(token, id)
    return JSONResponse(status_code=200, content={"message": "Succesfully removed the item from cart"})

@router.get("/cart", response_model=list[PublicOrder])
async def get_cart_r(token: Annotated[str, Depends(oauth2_scheme)]):
    cart = get_cart(token)
    return cart

@router.patch("/place-order")
async def place_order_r(token: Annotated[str, Depends(oauth2_scheme)]):
    place_order(token)
    return JSONResponse(status_code=200, content={"message": "Order placed succesfully"})
from app.database import get_session
from app.models import Product, User
from app.schemas import ProductCreate, ProductEdit, ProductRestock
from app.utilities import oauth2_scheme, validate_token
from fastapi import Depends, HTTPException
from typing import Annotated
from sqlalchemy import select


def list_product(data: ProductCreate, token: Annotated[str, Depends(oauth2_scheme)]):
    with get_session() as sesssion:
        payload = validate_token(token)
        if payload.get("role") == "customer":
            raise HTTPException(status_code=403, detail="User forbidden from perofroming this operation")
        username = payload.get("sub")
        stmt = select(User).where(User.name == username)
        user = sesssion.scalar(stmt)
        
        product = Product(
            name = data.name,
            description = data.description,
            price = data.price,
            quantity = data.quantity,
            seller_id = user.id
        )
        sesssion.add(product)
        sesssion.commit()
        
def edit_product(token: Annotated[str, Depends(oauth2_scheme)], edit_body: ProductEdit, id: int):
    with get_session() as session:
        payload = validate_token(token)
        
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        seller_id = product.seller_id
        user = session.get(User, seller_id)

        if payload.get("sub") != user.name:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        edit_product = edit_body.model_dump(exclude_unset=True)
        for key, value, in edit_product.items():
            setattr(product, key, value)

        session.commit()

def restock_product(token: Annotated[str, Depends(oauth2_scheme)], restock_body: ProductRestock, id: int):
    with get_session() as session:
        payload = validate_token(token)

        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        seller_id = product.seller_id
        user = session.get(User, seller_id)
        
        if payload.get("sub") != user.name:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        quantity = restock_body.quantity
        if quantity == 0:
            raise HTTPException(status_code=400, detail="Bad request, restock empty")
        if product.quantity + quantity < 0:
            raise HTTPException(status_code=400, detail="Bad request, restock negative")

        product.quantity += quantity
        session.commit()

def delete_product(token: Annotated[str, Depends(oauth2_scheme)], id: int):
    with get_session() as session:
        payload = validate_token(token)
        
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        seller_id = product.seller_id
        user = session.get(User, seller_id)

        if payload.get("sub") != user.name:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        session.delete(product)
        session.commit()

def get_product(id: int):
    with get_session() as session:
        product = session.get(Product, id)
        if not product:
            raise HTTPException(status_code=404, detail="Listing not found")
        return product

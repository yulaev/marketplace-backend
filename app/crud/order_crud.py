from app.database import get_session
from app.models import Product, User, Order, OrderItem, OrderStatus
from app.schemas import AddToCartBody
from app.utilities import oauth2_scheme, validate_token
from fastapi import Depends, HTTPException
from typing import Annotated
from sqlalchemy import select

def add_to_cart(token: Annotated[str, Depends(oauth2_scheme)], item_data: AddToCartBody):
    with get_session() as session:
        payload = validate_token(token)
        if payload.get("role") != "customer":
            raise HTTPException(status_code=403, detail="You are forbidden from performing this operation")
        
        u_stmt = select(User).where(User.name == payload.get("sub"))
        user = session.scalar(u_stmt)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        p_stmt = select(Product).where(Product.id == item_data.id)
        product = session.scalar(p_stmt)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if item_data.quantity > product.quantity:
            raise HTTPException(status_code=400, detail="Quantity exceeds available")

        o_stmt = select(Order).where(Order.customer_id == user.id, Order.status == OrderStatus.pending)
        order = session.scalar(o_stmt)
        if not order:
            order = Order (
                customer_id = user.id,
                status = OrderStatus.pending
            )

            session.add(order)
            session.commit()
        
        order_item = OrderItem (
            order_id = order.id,
            product_id = product.id,
            quantity = item_data.quantity,
            status = OrderStatus.pending
        )

        session.add(order_item)
        session.commit()

def remove_from_cart(token: Annotated[str, Depends(oauth2_scheme)], id: int):
    with get_session() as session:
        payload = validate_token(token)
        if payload.get("role") != "customer":
            raise HTTPException(status_code=403, detail="You are forbidden from performing this operation")
        
        u_stmt = select(User).where(User.name == payload.get("sub"))
        user = session.scalar(u_stmt)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        order_item = session.get(OrderItem, id)
        if not order_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        o_stmt = select(Order).where(Order.id == order_item.order_id, Order.status == OrderStatus.pending)
        order = session.scalar(o_stmt)
        if not order:
            raise HTTPException(status_code=404, detail="Cart not found(empty)")
        
        user_check = session.get(User, order.customer_id)
        if user.id != user_check.id:
            raise HTTPException(status_code=403, detail="You are forbidden from performing this operation")
        
        session.delete(order_item)
        session.commit()

def get_cart(token: Annotated[str, Depends(oauth2_scheme)]):
    with get_session() as session:
        payload = validate_token(token)

        u_stmt = select(User).where(User.name == payload.get("sub"))
        user = session.scalar(u_stmt)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        o_stmt = select(Order).where(Order.customer_id == user.id, Order.status == OrderStatus.pending)
        order = session.scalar(o_stmt)
        if not order:
            raise HTTPException(status_code=404, detail="Cart not found(empty)")
        
        i_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        cart = session.scalars(i_stmt).all()
        return cart
    
def update_order_status(cart: list[OrderItem]):
    status = min(cart, key=lambda item: item.status.priority).status
    return status
    
def place_order(token: Annotated[str, Depends(oauth2_scheme)]):
    with get_session() as session:
        payload = validate_token(token)

        u_stmt = select(User).where(User.name == payload.get("sub"))
        user = session.scalar(u_stmt)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        o_stmt = select(Order).where(Order.customer_id == user.id, Order.status == OrderStatus.pending)
        order = session.scalar(o_stmt)
        if not order:
            raise HTTPException(status_code=404, detail="Cart not found(empty)")
        
        i_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        cart = session.scalars(i_stmt).all()
        for item in cart:
            item.status = OrderStatus.ordered
            session.commit()

        order.status = update_order_status(cart)
        session.commit()
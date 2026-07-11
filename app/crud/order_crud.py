from app.database import get_session
from app.models import Product, User, Order, OrderItem, OrderStatus, UserRole
from app.schemas import AddToCartBody
from app.utilities import oauth2_scheme, validate_token
from fastapi import Depends, HTTPException
from typing import Annotated
from sqlalchemy import select

def add_to_cart(token: Annotated[str, Depends(oauth2_scheme)], item_data: AddToCartBody):
    with get_session() as session:
        payload = validate_token(token)
        if payload.get("role") != "customer":
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
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
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
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
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
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
    # i will probably forget what this does if i dont add this
    # basically min is being called on each items' in the cart priority
    # and then it returns the item with the lowest one, on which .status is then called
    status = min(cart, key=lambda item: item.status.priority).status
    return status
    
# Customer specific action
# First stage of the ordering process
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
        
        product_ids = [item.product_id for item in cart]
        p_stmt = select(Product).where(Product.id.in_(product_ids))
        products = session.scalars(p_stmt).all()
        
        for item, product in zip(cart,products):
            if item.quantity > product.quantity:
                raise HTTPException(status_code=400, detail="Item not available or quantity exceeds available")
        for item, product in zip(cart,products):
            product.quantity = product.quantity - item.quantity
            item.status = OrderStatus.ordered
            session.commit()

        order.status = update_order_status(cart)
        session.commit()

# Seller specific action
# Second stage of the ordering process
def mark_as_shipped(token: Annotated[str, Depends(oauth2_scheme)], id):
    with get_session() as session:
        payload = validate_token(token)

        u_stmt = select(User).where(User.name == payload.get("sub"))
        user = session.scalar(u_stmt)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role != UserRole.seller:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        i_stmt = select(OrderItem).where(OrderItem.id == id)
        item = session.scalar(i_stmt)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.status != OrderStatus.ordered:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        o_stmt = select(Order).where(Order.id == item.order_id)
        order = session.scalar(o_stmt)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        p_stmt = select(Product).where(Product.id == item.product_id)
        product = session.scalar(p_stmt)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if product.seller_id != user.id:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        item.status = OrderStatus.shipped

        c_stmt = select(OrderItem).where(OrderItem.order_id ==  order.id)
        cart = session.scalars(c_stmt).all()
        
        order.status = update_order_status(cart)
        session.commit()

# Customer specific action
# Final stage of the ordering process
def mark_as_delivered(token: Annotated[str, Depends(oauth2_scheme)], id):
    with get_session() as session:
        payload = validate_token(token)

        u_stmt = select(User).where(User.name == payload.get("sub"))
        user = session.scalar(u_stmt)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role != UserRole.customer:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        i_stmt = select(OrderItem).where(OrderItem.id == id)
        item = session.scalar(i_stmt)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.status != OrderStatus.shipped:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        o_stmt = select(Order).where(Order.id == item.order_id)
        order = session.scalar(o_stmt)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.customer_id != user.id:
            raise HTTPException(status_code=403, detail="User forbidden from performing this operation")
        
        item.status = OrderStatus.delivered

        c_stmt = select(OrderItem).where(OrderItem.order_id ==  order.id)
        cart = session.scalars(c_stmt).all()
        
        order.status = update_order_status(cart)
        session.commit()
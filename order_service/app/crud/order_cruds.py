from sqlmodel import Session, select # type: ignore
from app.models.order_model import Order,UpdateOrder
from fastapi import HTTPException # type: ignore



# def add_order(session: Session, order: Order) -> Order:
#     session.add(order)
#     session.commit()
#     session.refresh(order)
#     return order

def create_order(session: Session, order: Order, product_price: float):
    order.total_price = order.quantity * product_price  # Calculate total price
    session.add(order)
    session.commit()
    session.refresh(order)
    return order

def get_order(session: Session, order_id: int) -> Order:
    return session.get(Order, order_id)

def get_all_orders(session: Session, user_id: int) -> list[Order]:
    statement = select(Order).where(Order.user_id == user_id)
    return session.exec(statement).all()

def update_order(session: Session, order_id: int,to_update_order : UpdateOrder) -> Order:   # status: str
    # Step 1: Get the Product by ID
    order = session.exec(select(Order).where(Order.id == order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Product not found")
    # Step 2: Update the Product
    hero_data = to_update_order.model_dump(exclude_unset=True)
    order.sqlmodel_update(hero_data)
    session.add(order)
    session.commit()
    return order

def update_order_status(session: Session, order_id: int, status: str):
    order = session.get(Order, order_id)
    if order:
        order.status = status
        session.add(order)
        session.commit()
        session.refresh(order)
    return order

def delete_order(session: Session, order_id: int) -> None:
    order = session.get(Order, order_id)
    if order is None: 
        return HTTPException(status_code=404, detail="Product not found")
    session.delete(order)
    session.commit()
    return {"message": "Product Deleted Successfully"}


from sqlmodel import Session, select # type: ignore
from app.models.order_model import Order,OrderUpdate
from fastapi import HTTPException # type: ignore
import requests
from app.db_engine import engine
from aiokafka import AIOKafkaProducer #type:ignore
from app.consumer.order_status_update import consume_payment_response_message



def send_order_to_kafka(session: Session, order: Order, product_price: float):
    order.total_price = order.quantity * product_price  # Calculate total price
    return order

def place_order(session: Session, order: Order, product_price: float):
    order.total_price = order.quantity * product_price  # Calculate total price
    order.status = "Unpaid"  # Set default status to "Unpaid"
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def get_order(session: Session, order_id: int, user_id: int) -> Order:
    order = session.exec(select(Order).where(Order.id == order_id, Order.user_id == user_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found or not authorized")
    return order

def get_all_orders(session: Session, user_id: int) -> list[Order]:
    statement = select(Order).where(Order.user_id == user_id)
    return session.exec(statement).all()

def update_order(session: Session, order_id: int, user_id: int, to_update_order: OrderUpdate) -> Order:
    order = get_order(session, order_id, user_id)
    hero_data = to_update_order.dict(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(order, key, value)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def update_order_status(session: Session, order_id: int, user_id: int, status: str):
    order = get_order(session, order_id, user_id)
    order.status = status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def delete_order(session: Session, order_id: int, user_id: int):
    order = get_order(session, order_id, user_id)
    session.delete(order)
    session.commit()
    return {"message": "Order deleted successfully"}



def get_product_price(product_id: int) -> float:
    # Fetch product price from Product Service
    response = requests.get(f'http://product-service-api:8003/products/{product_id}')
    response_data = response.json()
    return response_data['price']





# def process_payment_event(payment_data):
#     with Session(engine) as session:
#         order = session.exec(select(Order).where(Order.id == payment_data["order_id"])).one_or_none()
#         if order:
#             order.status = "Paid"
#             session.add(order)
#             session.commit()
#             session.refresh(order)
#             # Produce event to update inventory
#             event = {
#                 "order_id": order.id,
#                 "product_id": order.product_id,
#                 "quantity": order.quantity,
#                 "status": "Paid"
#             }
#             produce_event("order_paid", event)


# async def produce_event(topic, event):
#     producer = AIOKafkaProducer(bootstrap_servers='broker:19092')
#     await producer.start()
#     try:
#         await producer.send_and_wait(topic, json.dumps(event).encode('utf-8'))
#     finally:
#         await producer.stop()           
            
# if __name__ == "__main__":
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(consume_payment_response_message())


# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from sqlmodel import Field, Session, SQLModel, select, Sequence # type: ignore
from fastapi import FastAPI, Depends,HTTPException # type: ignore
from typing import AsyncGenerator
# from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
import asyncio
import json
from app import settings
from app.db_engine import engine
from app.deps import get_kafka_producer,get_session
from app.models.order_model import Order,UpdateOrder
from app.crud.order_cruds import add_order,get_all_orders,get_order,delete_order,update_order
import requests


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

#
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables....")
    # task = asyncio.create_task(consume_messages(settings.KAFKA_ORDER_TOPIC, 'broker:19092'))
    create_db_and_tables()
    yield 


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    # servers=[
    #     {
    #         "url": "http://127.0.0.1:8000", # ADD NGROK URL Here Before Creating GPT Action
    #         "description": "Development Server"
    #     }
    #     ]
        )

def get_product_price(product_id: int) -> float:
    # Fetch product price from Product Service
    response = requests.get(f'http://product-service-api:8003/products/{product_id}')
    response_data = response.json()
    return response_data['price']

# Root endpoint
@app.get("/")
def read_root():
    return {"Welcome": "order_service"}


@app.post("/orders/", response_model=Order)
async def create_order(order:Order, session: Annotated[Session, Depends(get_session)],producer:Annotated[AIOKafkaProducer,Depends(get_kafka_producer)]):
    product_price = get_product_price(order.product_id)
    new_order = add_order(session, order)

    order_dict = {field: getattr(order, field) for field in order.dict()}
    order_json = json.dumps(order_dict).encode("utf-8")
    print("orderJSON:", order_json)
    # Produce message
    await producer.send_and_wait("order_placed", order_json)
    return new_order

@app.get("/orders/{order_id}", response_model=Order)
def read_order(order_id: int, session: Session = Depends(get_session)):
    order = get_order(session, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/orders/", response_model=list[Order])
def list_orders(user_id: int, session: Session = Depends(get_session)):
    return get_all_orders(session, user_id)

@app.patch("/orders/{order_id}", response_model=UpdateOrder)
def update_order_status(order_id: int,order:UpdateOrder, session: Annotated[Session, Depends(get_session)]):
    try:
        return update_order(session=session, order_id=order_id,to_update_order=order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/orders/{order_id}")
def delete_order_by_id(order_id: int,session: Annotated[Session, Depends(get_session)]):
    try:
        return delete_order(session=session, order_id=order_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.patch("/orders/{order_id}", response_model=Order)
def update_order(order_id: int, status: str, session: Annotated[Session, Depends(get_session)]):
    order = update_order_status(session, order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order        



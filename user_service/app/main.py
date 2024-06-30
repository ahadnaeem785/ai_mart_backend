# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from sqlmodel import Field, Session, SQLModel, select, Sequence
from fastapi import FastAPI, Depends,HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaConsumer,AIOKafkaProducer
import asyncio
import json
from app import settings
from app.db_engine import engine
from app.deps import get_kafka_producer,get_session
from app.models.user_model import User,UserUpdate
from app.crud.user_crud import add_new_user,get_user_by_id,get_all_users,delete_user_by_id,update_user_by_id


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

# async def consume_messages(topic, bootstrap_servers):
#     # Create a consumer instance.
#     consumer = AIOKafkaConsumer(
#         topic,
#         bootstrap_servers=bootstrap_servers,
#         group_id="product_consumer_group",
#         auto_offset_reset='earliest'
#     )

#     # Start the consumer.
#     await consumer.start()
#     try:
#         # Continuously listen for messages.
#         async for message in consumer:
#             print("RAW")
#             print(f"Received message on topic {message.topic}")

#             product_data = json.loads(message.value.decode())
#             print("TYPE", (type(product_data)))
#             print(f"Product Data {product_data}")


            
#             with next(get_session()) as session:
#                 print("SAVING DATA TO DATABSE")
#                 db_insert_product = add_new_product(
#                     product_data=Product(**product_data), session=session)
#                 print("DB_INSERT_PRODUCT", db_insert_product)
                
#             # print(f"Received message: {message.value.decode()} on topic {message.topic}")
#             # Here you can add code to process each message.
#             # Example: parse the message, store it in a database, etc.
#     finally:
#         # Ensure to close the consumer when done.
#         await consumer.stop()


# # The first part of the function, before the yield, will
# # be executed before the application starts.
# # https://fastapi.tiangolo.com/advanced/events/#lifespan-function
# # loop = asyncio.get_event_loop()
@asynccontextmanager
async def lifespan(app: FastAPI)-> AsyncGenerator[None, None]:
    print("Creating tables..")
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



@app.get("/")
def read_root():
    return {"User": "Service"}


@app.post("/users/", response_model=User)
def create_new_user(user_data: User, session: Annotated[Session, Depends(get_session)]):
    new_user = add_new_user(user_data=user_data, session=session)
    return new_user

@app.get("/users/", response_model=list[User])
def read_users(session: Annotated[Session, Depends(get_session)]):
    """ Get all users from the database"""
    return get_all_users(session)

@app.get("/users/{user_id}", response_model=User)
def read_single_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """Read a single user"""
    try:
        return get_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Delete a single user by ID"""
    try:
        return delete_user_by_id(user_id=user_id, session=session)
    except HTTPException as e:
        raise e

@app.patch("/users/{user_id}", response_model=UserUpdate)
def update_single_user(user_id: int, user: UserUpdate, session: Annotated[Session, Depends(get_session)]):
    """ Update a single user by ID"""
    try:
        return update_user_by_id(user_id=user_id, to_update_user_data=user, session=session)
    except HTTPException as e:
        raise e

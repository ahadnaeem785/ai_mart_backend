# main.py
from datetime import timedelta
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
from app.models.user_model import User,UserUpdate,Register_User,Token
from app.crud.user_crud import add_new_user,get_user_by_id,get_all_users,delete_user_by_id,update_user_by_id
from app.auth import get_user_from_db ,hash_password,authenticate_user,EXPIRY_TIME,create_access_token
from fastapi.security import OAuth2PasswordRequestForm

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)

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


# @app.post("/users/", response_model=User)
# def create_new_user(user_data: User, session: Annotated[Session, Depends(get_session)]):
#     new_user = add_new_user(user_data=user_data, session=session)
#     return new_user

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


#signup user if not already signed up
@app.post("/register")
async def regiser_user(new_user:Annotated[Register_User, Depends()],
                        session:Annotated[Session, Depends(get_session)]):
    db_user = get_user_from_db(session, new_user.username, new_user.email)
    if db_user:
        raise HTTPException(status_code=409, detail="User with these credentials already exists")
    user = User(
                username = new_user.username,
                email = new_user.email,
                password = hash_password(new_user.password))

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": f""" {user.username} successfully registered """}    



# login user with username and password
@app.post('/token')
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()],
                session:Annotated[Session, Depends(get_session)]):
    user = authenticate_user (form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    expire_time = timedelta(minutes=EXPIRY_TIME)
    access_token = create_access_token({"sub":form_data.username}, expire_time)
    
    return Token(access_token=access_token, token_type="bearer")
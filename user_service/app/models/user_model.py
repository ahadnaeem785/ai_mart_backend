from sqlmodel import SQLModel,Field
from typing import Optional


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    # updated_at: datetime = Field(default_factory=datetime.utcnow)

class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    hashed_password: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


from datetime import datetime
from sqlmodel import SQLModel, Field # type: ignore



class Order(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    product_id: int
    user_id: int
    total_price: float
    quantity: int
    status: str
    # created_at: datetime = Field(default_factory=datetime.utcnow)
    # updated_at: datetime = Field(default_factory=datetime.utcnow)

    # items: list[OrderItem] = Relationship(back_populates="order")


class UpdateOrder(SQLModel):
    product_id: int
    user_id: int
    quantity: int
    total_price: float
    status: str
    # created_at: datetime = Field(default_factory=datetime.utcnow)



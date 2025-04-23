import datetime
import uuid

from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: uuid.UUID | None = Field(default=None, primary_key=True)
    user_alias: str


class Restaurant(SQLModel, table=True):
    id: uuid.UUID | None = Field(default=None, primary_key=True)
    name: str
    latitude: float
    longitude: float


class UserRestaurantNotation(SQLModel, table=True):
    id: uuid.UUID | None = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    restaurant_id: uuid.UUID = Field(foreign_key="restaurant.id")
    notation_date: datetime.datetime = Field(default=datetime.datetime.now(datetime.UTC))
    visit_date: datetime.datetime | None = Field(default=None)




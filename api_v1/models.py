import datetime
import uuid
import json

import sqlalchemy as sa
from geoalchemy2 import Geometry, WKBElement, Geography
from sqlmodel import SQLModel, Field, Column, Session
from geojson_pydantic import Point
from pydantic import field_validator

from .database import engine
from .constants import WORLD_GEODETIC_CRS


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_alias: str


class Restaurant(SQLModel, table=True):
    __tablename__ = "restaurants"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    coordinates: Point = Field(sa_column=Column(Geography(geometry_type='POINT', srid=WORLD_GEODETIC_CRS)))

    #class Config:
    #    arbitrary_types_allowed = True


class UserRestaurantRating(SQLModel, table=True):
    __tablename__ = "user_restaurant_ratings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    restaurant_id: uuid.UUID = Field(foreign_key="restaurants.id")
    rating_date: datetime.datetime = Field(default=datetime.datetime.now(datetime.UTC))
    visit_date: datetime.datetime | None = Field(default=None)
    rating: int

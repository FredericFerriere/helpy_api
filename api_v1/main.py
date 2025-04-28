from fastapi import FastAPI
from sqlmodel import Session, select

from .database import engine
from .models import Restaurant
from geoalchemy2 import functions

app = FastAPI()

@app.get('/')
def get_root():
    return {"a":"b"}

@app.get('/users/{user_id}/restaurants/top/')
async def get_top_restaurants_user(user_id: str):
    with Session(engine) as session:
#        print('ok')
#        statement = select(Restaurant, UserRestaurantNotation).where(UserRestaurantNotation.restaurant_id==Restaurant.id)
#        results = session.exec(statement, functions.ST_AsGeoJSON(Restaurant.coordinates))
        statement = select(Restaurant).where(Restaurant.name == "restaurant_42")
        results = session.exec(statement)
        res = [restaurant for restaurant in results]
    return res

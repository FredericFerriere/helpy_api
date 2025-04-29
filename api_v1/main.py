from fastapi import FastAPI
from sqlmodel import Session, select

from .database import engine
from .models import Restaurant, UserRestaurantNotation
from geoalchemy2.shape import to_shape

app = FastAPI()

@app.get('/')
def get_root():
    return {"a":"b"}

@app.get('/users/{user_id}/restaurants/top/')
async def get_top_restaurants_user(user_id: str):
    with Session(engine) as session:
        statement = select(Restaurant, UserRestaurantNotation).join(UserRestaurantNotation).where(
            UserRestaurantNotation.user_id==user_id)
        results = session.exec(statement)
        res=[]
        for restaurant, notation in results:
            res.append({'name': restaurant.name,
                        'notation': notation.notation,
                        'user_id': notation.user_id,
                        'location': to_shape(restaurant.coordinates).wkt})
        return res

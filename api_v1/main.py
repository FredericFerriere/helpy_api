from fastapi import FastAPI, Query
from sqlmodel import Session, select

from .database import engine
from .models import Restaurant, UserRestaurantNotation
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_Buffer, ST_GeogFromText, ST_Distance

app = FastAPI()

@app.get('/')
def get_root():
    return {"a":"b"}

@app.get('/users/{user_id}/restaurants/my_notations')
async def get_known_restaurants_user(user_id: str):
    with Session(engine) as session:
        statement = select(Restaurant, UserRestaurantNotation).join(UserRestaurantNotation).where(
            UserRestaurantNotation.user_id==user_id)
        results = session.exec(statement)
        res = []
        for restaurant, notation in results:
            res.append({'name': restaurant.name,
                        'notation': notation.notation,
                        'user_id': notation.user_id,
                        'location': to_shape(restaurant.coordinates).wkt})
        return res

@app.get('/users/{user_id}/restaurants/suggestions')
async def get_restaurant_suggestions_user(user_id,
                                          latitude: float = Query(ge=-90, le=90),
                                          longitude: float = Query(ge=-180, le=180),
                                          radius: int = Query(ge=1)):
    with Session(engine) as session:
        statement = select(Restaurant).where(ST_Distance(Restaurant.coordinates,
                            ST_GeogFromText('SRID=4326;POINT({} {})'.format(longitude, latitude)))<radius)
        results = session.exec(statement)
        res = []
        for restaurant in results:
            res.append({'name': restaurant.name,
                        'location': to_shape(restaurant.coordinates).wkt})
        return res


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from sqlmodel import Session, select, func

from .database import engine
from .models import Restaurant, UserRestaurantRating
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_Buffer, ST_GeogFromText, ST_Distance

app = FastAPI()

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def get_root():
    return {"a":"b"}

@app.get('/users/{user_id}/restaurants/my_notations')
async def get_known_restaurants_user(user_id: str):
    with Session(engine) as session:
        statement = select(Restaurant, UserRestaurantRating).join(UserRestaurantRating).where(
            UserRestaurantRating.user_id==user_id)
        results = session.exec(statement)
        res = []
        for restaurant, rating in results:
            res.append({'name': restaurant.name,
                        'notation': rating.rating,
                        'user_id': rating.user_id,
                        'location': to_shape(restaurant.coordinates).wkt})
        return res

@app.get('/users/{user_id}/restaurants/geographic_filter/')
async def get_restaurant_suggestions_user(user_id,
                                          latitude: float = Query(ge=-90, le=90),
                                          longitude: float = Query(ge=-180, le=180),
                                          radius: int = Query(ge=1, le=10000)):
    with Session(engine) as session:
        statement = select(
            Restaurant.id,
            Restaurant.name,
            Restaurant.coordinates,
            func.avg(UserRestaurantRating.rating).label('average_rating')
        ).join(UserRestaurantRating).where(
            ST_Distance(Restaurant.coordinates, ST_GeogFromText('SRID=4326;POINT({} {})'
                                                                   .format(longitude, latitude)))<radius
               ).group_by(Restaurant.id)
        results = session.exec(statement)
        res = [{'id': restaurant_id,
                'name': restaurant_name,
                'location': to_shape(location).wkt,
                'average_rating': round(rating,1)}
               for restaurant_id, restaurant_name, location, rating in results]
        return res


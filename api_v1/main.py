import uuid
from datetime import datetime
import logging

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlmodel import Session, select, func

from .database import engine
from .models import User, Restaurant, UserRestaurantRating
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_GeogFromText, ST_Distance
from .record_manager import RecordManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    return {"a": "b"}


@app.get('/users/{user_id}/restaurants/my_notations')
async def get_known_restaurants_user(user_id: str):
    '''

    :param user_id: INFER FROM JWT
    :return:
    '''
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
    '''

    :param user_id: INFER FROM JWT
    :param latitude:
    :param longitude:
    :param radius:
    :return:
    '''
    with Session(engine) as session:
        statement = select(
            Restaurant.id,
            Restaurant.name,
            Restaurant.coordinates,
            func.avg(UserRestaurantRating.rating).label('average_rating')
        ).join(UserRestaurantRating).where(
            ST_Distance(Restaurant.coordinates, ST_GeogFromText('SRID=4326;POINT({} {})'
                                                                   .format(longitude, latitude))) < radius
               ).group_by(Restaurant.id)
        results = session.exec(statement)
        res = [{'id': restaurant_id,
                'name': restaurant_name,
                'location': to_shape(location).wkt,
                'average_rating': round(rating,1)}
               for restaurant_id, restaurant_name, location, rating in results]
        return res

@app.post('/users/{user_id}/restaurants/new_rating/')
async def put_restaurant_rating(user_id: uuid.UUID, restaurant_id: uuid.UUID, rating: int = Query(ge=1, le=10),
                                rating_date: datetime = datetime.now(), visit_date: datetime | None = None):
    """
    :param user_id: INFER FROM JWT
    :param restaurant_id:
    :param rating:
    :param rating_date:
    :param visit_date:
    :return:
    """

    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        restaurant = session.get(Restaurant, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        new_rating = UserRestaurantRating(user_id=user_id, restaurant_id=restaurant_id, rating=rating,
                                          rating_date=rating_date, visit_date=visit_date)
        RecordManager.add_record(new_rating)
        return new_rating

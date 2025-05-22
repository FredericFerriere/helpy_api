import logging
import uuid
from datetime import datetime

from fastapi import Query, HTTPException
from sqlmodel import select, func
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_GeogFromText, ST_Distance

from .app_utility import create_app
from .models import User, Restaurant, UserRestaurantRating
from .session_manager import SessionManager
from .database_utility import add_record


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = create_app()


@app.get('/')
def get_root():
    return {"a": "b"}


@app.get('/users/{user_id}/restaurants/my_notations')
async def get_known_restaurants_user(user_id: uuid.UUID):
    with SessionManager.create_session() as session:
        statement = select(Restaurant, UserRestaurantRating).join(UserRestaurantRating).where(
            UserRestaurantRating.user_id == user_id)
        results = session.exec(statement)
        res = []
        for restaurant, rating in results:
            res.append({'name': restaurant.name,
                        'notation': rating.rating,
                        'user_id': rating.user_id,
                        'location': to_shape(restaurant.coordinates).wkt})
        return res


@app.get('/users/{user_id}/restaurants/geographic_filter/')
async def get_restaurant_suggestions_user(user_id: uuid.UUID, latitude: float = Query(ge=-90, le=90),
                                        longitude: float = Query(ge=-180, le=180), radius: int = Query(ge=1, le=10000)):
    with SessionManager.create_session() as session:
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
                'average_rating': round(rating, 1)}
               for restaurant_id, restaurant_name, location, rating in results]
        return res


@app.post('/users/{user_id}/restaurants/new_rating/')
async def add_restaurant_rating(user_id: uuid.UUID, restaurant_id: uuid.UUID, rating: int = Query(ge=1, le=10),
                              rating_date: datetime = datetime.now(), visit_date: datetime | None = None):
    with SessionManager.create_session() as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        restaurant = session.get(Restaurant, restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        new_rating = UserRestaurantRating(user_id=user_id, restaurant_id=restaurant_id, rating=rating,
                                          rating_date=rating_date, visit_date=visit_date)
        add_record(session, new_rating)
        return new_rating

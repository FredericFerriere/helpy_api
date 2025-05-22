import uuid
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select, Session, func
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_GeogFromText, ST_Distance

from .database_manager import DatabaseManager
from .models import User, Restaurant, UserRestaurantRating


class AppManager:

    @staticmethod
    def create_app():
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
        return app

    @staticmethod
    def get_known_restaurants_user(user_id: uuid.UUID):
        with Session(DatabaseManager.engine) as session:
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

    @staticmethod
    def get_restaurant_suggestions_user(user_id: uuid.UUID, latitude: float = Query(ge=-90, le=90),
                                        longitude: float = Query(ge=-180, le=180), radius: int = Query(ge=1, le=10000)):
        '''

        :param user_id: INFER FROM JWT
        :param latitude:
        :param longitude:
        :param radius:
        :return:
        '''
        with Session(DatabaseManager.engine) as session:
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

    @staticmethod
    def put_restaurant_rating(user_id: uuid.UUID, restaurant_id: uuid.UUID, rating: int = Query(ge=1, le=10),
                              rating_date: datetime = datetime.now(), visit_date: datetime | None = None):
        """
        :param user_id: INFER FROM JWT
        :param restaurant_id:
        :param rating:
        :param rating_date:
        :param visit_date:
        :return:
        """

        with Session(DatabaseManager.engine) as session:
            user = session.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            restaurant = session.get(Restaurant, restaurant_id)
            if not restaurant:
                raise HTTPException(status_code=404, detail="Restaurant not found")

            new_rating = UserRestaurantRating(user_id=user_id, restaurant_id=restaurant_id, rating=rating,
                                              rating_date=rating_date, visit_date=visit_date)
            DatabaseManager.add_record(new_rating)
            return new_rating

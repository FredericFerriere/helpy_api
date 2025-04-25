import math
from random import random, randint, sample
from shapely.geometry import Point
import geopandas

from sqlmodel import Session

from .models import User, Restaurant, UserRestaurantNotation
from .database import engine, create_db_and_tables

def generate_random_point(latitude, longitude, max_radius):
    s = geopandas.GeoSeries([Point(longitude, latitude)], crs=4326)
    s = s.to_crs(3857)
    rand_radius = max_radius * random()
    rand_angle = 2 * math.pi * random()
    ref_point = s.to_list()[0]
    new_point = Point(ref_point.x + rand_radius * math.cos(rand_angle), ref_point.y + rand_radius * math.sin(rand_angle))
    o = geopandas.GeoSeries([new_point], crs=3857)
    o = o.to_crs(4326)
    new_point = o.to_list()[0]
    return new_point.y, new_point.x

def create_sample():
    num_users = 1000
    num_restaurants = 100
    min_eval = 3
    max_eval = 6
    users = []
    restaurants = []
    cities = [[48.8620625, 2.3427284, 5000], [45.90751266479492, 6.124344348907471, 3000]]

    with Session(engine) as session:
        for j in range(num_restaurants):
            city_pick = cities[0 if random()<0.8 else 1]
            latitude = city_pick[0]
            longitude = city_pick[1]
            radius = city_pick[2]
            lat, lon = generate_random_point(latitude, longitude, radius)

            restaurant = Restaurant(name='restaurant_{}'.format(j), coordinates='POINT({} {})'.format(lon, lat))
            session.add(restaurant)
            session.commit()
            session.refresh(restaurant)
            restaurants.append(restaurant)

        for i in range(num_users):
            user = User(user_alias='dummy_{}'.format(i))
            session.add(user)
            session.commit()
            session.refresh(user)
            users.append(user)

            num_eval = randint(min_eval, max_eval)
            rest_ids = sample(range(num_restaurants), num_eval)
            for el in rest_ids:
                restaurant = restaurants[el]
                notation = UserRestaurantNotation(user_id=user.id, restaurant_id = restaurant.id, notation=randint(1,10))
                session.add(notation)
                session.commit()


def main():
    create_db_and_tables()
    create_sample()

if __name__ == "__main__":
    main()
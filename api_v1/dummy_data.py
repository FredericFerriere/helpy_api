import math
from random import random, randint, sample

from shapely.geometry import Point
import geopandas

from .models import User, Restaurant, UserRestaurantRating
from .database_utility import add_record, create_db_and_tables
from .constants import PROJECTED_MERCATOR_CRS, WORLD_GEODETIC_CRS
from .session_manager import SessionManager


def generate_random_point(latitude: float, longitude: float, max_radius: float):
    """
    Generates a random point around (latitude, longitude) within a max_radius distance.
    Initial coordinates are geodetic so they need to be converted to a projected system (e.g. Projected Mercator).
    From there we are in a cartesian plane and can generate a random point around the initial point.
    The result is converted back to geodetic type coordinates (crs code 4326) using geopandas GeoSeries crs
    :param latitude: latitude in standard geodetic system (crs code 4326)
    :param longitude: longitude in standard geodetic system (crs code 4326)
    :param max_radius: expressed in meters
    :return: (new_latitude, new_longitude)
    """

    # Conversion to projected type
    s = geopandas.GeoSeries([Point(longitude, latitude)], crs=WORLD_GEODETIC_CRS)
    s = s.to_crs(PROJECTED_MERCATOR_CRS)
    ref_point = s.to_list()[0]

    # Generate random point around coordinates
    rand_radius = max_radius * random()
    rand_angle = 2 * math.pi * random()
    new_point = Point(ref_point.x + rand_radius * math.cos(rand_angle), ref_point.y + rand_radius * math.sin(rand_angle))

    # Convert back to initial coordinated reference system
    o = geopandas.GeoSeries([new_point], crs=PROJECTED_MERCATOR_CRS)
    o = o.to_crs(WORLD_GEODETIC_CRS)
    new_point = o.to_list()[0]
    return new_point.y, new_point.x


def create_sample():
    num_users = 100
    num_restaurants = 10
    min_eval = 3
    max_eval = 6
    users = []
    restaurants = []
    cities = [[48.8620625, 2.3427284, 5000], [45.90751266479492, 6.124344348907471, 3000]]

    with SessionManager.create_session() as session:
        for j in range(num_restaurants):
            city_pick = cities[0 if random() < 0.8 else 1]
            latitude = city_pick[0]
            longitude = city_pick[1]
            radius = city_pick[2]
            lat, lon = generate_random_point(latitude, longitude, radius)

            restaurant = Restaurant(name='restaurant_{}'.format(j), coordinates='POINT({} {})'.format(lon, lat))
            add_record(session, restaurant)
            restaurants.append(restaurant)

        for i in range(num_users):
            user = User(user_alias='dummy_{}'.format(i))
            add_record(session, user)
            users.append(user)

            num_eval = randint(min_eval, max_eval)
            rest_ids = sample(range(num_restaurants), num_eval)
            for el in rest_ids:
                restaurant = restaurants[el]
                rating = UserRestaurantRating(user_id=user.id, restaurant_id=restaurant.id, rating=randint(1, 10))
                add_record(session, rating)


def main():
    create_db_and_tables()
    create_sample()
    return


if __name__ == "__main__":
    main()

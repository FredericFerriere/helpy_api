import logging

from .app_manager import AppManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = AppManager.create_app()


@app.get('/')
def get_root():
    return {"a": "b"}


@app.get('/users/{user_id}/restaurants/my_notations')
async def get_known_restaurants_user(user_id):
    return AppManager.get_known_restaurants_user(user_id)


@app.get('/users/{user_id}/restaurants/geographic_filter/')
async def get_restaurant_suggestions_user(user_id, latitude, longitude, radius):
    return AppManager.get_restaurant_suggestions_user(user_id, latitude, longitude, radius)


@app.post('/users/{user_id}/restaurants/new_rating/')
async def put_restaurant_rating(user_id, restaurant_id, rating, rating_date, visit_date):
    return AppManager.put_restaurant_rating(user_id, restaurant_id, rating, rating_date, visit_date)

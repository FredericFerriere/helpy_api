from fastapi import FastAPI

app = FastAPI()


@app.get('users/{user_id}/restaurants/top/')
async def get_restaurants(user_id: str):
    return 6


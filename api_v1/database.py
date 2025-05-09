import os
from dotenv import load_dotenv

from sqlalchemy import URL
from sqlmodel import SQLModel, create_engine

load_dotenv()

url_object = URL.create(
    os.getenv('DB_DRIVER'),
    username=os.getenv('DB_USER'),
    password=os.getenv('DB_PWD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    database=os.getenv('DB_NAME'),
)

engine = create_engine(url_object, plugins=["geoalchemy2"])

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


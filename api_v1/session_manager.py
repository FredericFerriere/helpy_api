import os
from dotenv import load_dotenv

from sqlmodel import Session, create_engine
from sqlalchemy import URL


def initialise_engine():
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
    return engine


class SessionManager:
    engine = initialise_engine()

    @staticmethod
    def create_session():
        return Session(SessionManager.engine)

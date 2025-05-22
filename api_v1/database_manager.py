import os
from dotenv import load_dotenv

import logging

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy import URL


logger = logging.getLogger(__name__)


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


class DatabaseManager:
    engine = initialise_engine()

    @staticmethod
    def create_db_and_tables():
        SQLModel.metadata.create_all(DatabaseManager.engine)

    @staticmethod
    def add_record(record: SQLModel):
        try:
            session = Session(DatabaseManager.engine)
            session.add(record)
            session.commit()
            session.refresh(record)
        except Exception as error:
            logger.log(level=logging.INFO, msg="DB update error", exc_info=True)

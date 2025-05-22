import logging

from sqlmodel import Session, SQLModel

from .database import engine

logger = logging.getLogger(__name__)


class RecordManager:

    @staticmethod
    def add_record(record: SQLModel):
        try:
            session = Session(engine)
            session.add(record)
            session.commit()
            session.refresh(record)
        except Exception as error:
            logger.log(level=logging.INFO, msg="DB update error", exc_info=True)

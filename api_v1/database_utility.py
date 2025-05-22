import logging

from sqlmodel import Session, SQLModel

from .session_manager import SessionManager

logger = logging.getLogger(__name__)


def create_db_and_tables():
    SQLModel.metadata.create_all(SessionManager.engine)


def add_record(session: Session, record: SQLModel):
    try:
        session.add(record)
        session.commit()
        session.refresh(record)
    except Exception as error:
        logger.log(level=logging.INFO, msg="DB update error", exc_info=True)

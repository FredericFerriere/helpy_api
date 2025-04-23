from sqlmodel import Session

from .models import User
from .database import engine, create_db_and_tables

def create_user():
    with Session(engine) as session:
        user_1 = User(user_alias = 'dummy_a')
        session.add(user_1)
        session.commit()

def main():
    create_db_and_tables()
    create_user()


if __name__ == "__main__":
    main()
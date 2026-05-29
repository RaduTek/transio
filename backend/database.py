import os

from sqlalchemy import create_engine
from sqlmodel import Session


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://transio:transio@localhost:5432/transio",
)


engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def get_db():
    with Session(engine) as db:
        yield db

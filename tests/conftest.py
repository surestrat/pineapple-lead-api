from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from app.core.config import settings
from app.db.base import Base

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(settings.DATABASE_URL)
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=db_engine)()

    Base.metadata.create_all(bind=db_engine)

    yield session

    session.close()
    transaction.rollback()
    connection.close()
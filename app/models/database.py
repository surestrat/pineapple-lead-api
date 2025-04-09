from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create a metadata object
metadata = MetaData()

# Create a base class for declarative class definitions
Base = declarative_base(metadata=metadata)

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Create an engine
if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL.replace("postgresql+asyncpg", "postgresql"), echo=False
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None

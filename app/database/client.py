from sqlalchemy import create_engine
from config import settings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.POSTGRES_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

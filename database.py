from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
import os

SQLALCHEMY_DATABASE_URL = os.environ.get('db_url')

engine = create_engine(SQLALCHEMY_DATABASE_URL)


Sessionlocal = sessionmaker(autocommit= False , autoflush=False, bind=engine) 

Base = declarative_base()
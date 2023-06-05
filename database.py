import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import dotenv


SQLALCHEMY_DATABASE_URL = os.environ.get('db_url')
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:test1234!@localhost/TodoApplication'

dotenv.load_dotenv('.env')
engine = create_engine(SQLALCHEMY_DATABASE_URL)


Sessionlocal = sessionmaker(autocommit= False , autoflush=False, bind=engine) 

Base = declarative_base()
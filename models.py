from sqlalchemy import ARRAY, Boolean, Column, ForeignKey, Integer, String

from database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)


class Lists(Base):
    __tablename__ = "lists"
    id = Column(Integer, primary_key=True)
    listname = Column(String)
    list_owner = Column(Integer, ForeignKey("users.id"))
    shared_with = Column(ARRAY(String))


class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_list = Column(Integer, ForeignKey("lists.id"))
    # shared_with = Column(String , ForeignKey("users.username"))

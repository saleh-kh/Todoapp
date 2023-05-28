from database import Base
from sqlalchemy import Column,Integer , String , Boolean , ForeignKey





class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String,unique=True)
    hashed_password = Column(String)
    role = Column(String)




class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True )
    title = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean , default=False)
    owner_id = Column(Integer,ForeignKey("users.id"))
    # shared_with = Column(String , ForeignKey("users.username"))





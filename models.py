from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from database import engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class TaskDB(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True,autoincrement=True)
    title = Column(String)
    name = Column(String)
    completed = Column(Boolean, default=False)
    user_id=Column(Integer,ForeignKey("Users.id"))
    user=relationship("UserDB")

class UserDB(Base):
    __tablename__="Users"

    id=Column(Integer,primary_key=True,index=True,autoincrement=True)
    email=Column(String,unique=True,index=True)
    password=Column(String)
    

# Create table
Base.metadata.create_all(bind=engine)
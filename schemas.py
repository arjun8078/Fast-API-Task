from pydantic import BaseModel

class Task(BaseModel):
    
    title:str
    name:str 
    completed:bool

class User(BaseModel):
    email:str
    password:str
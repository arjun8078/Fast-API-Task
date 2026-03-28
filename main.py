from fastapi import FastAPI
from pydantic import BaseModel
from database import SessionLocal
from models import TaskDB,UserDB
from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime,timedelta
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

SECRET_KEY = "mysecretkey"   # later store in env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()


class Task(BaseModel):
    
    title:str
    name:str 
    completed:bool

class User(BaseModel):
    email:str
    password:str

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth2_schema=OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data:dict):
    to_encode=data.copy()

    exp_time=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp":exp_time})

    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

    return encoded_jwt





def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_current_user(token:str = Depends(oauth2_schema)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        email=payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        
        return email

    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")
    




@app.post("/tasks")
def create_task(task: Task,current_user:str=Depends(get_current_user)):
    db = SessionLocal()

    db_task = TaskDB(
       
        title=task.title,
        name=task.name,
        completed=task.completed
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task

@app.get("/tasks")
def get_tasks(current_user:str=Depends(get_current_user)):
    db = SessionLocal()
    tasks = db.query(TaskDB).all()
    return tasks

@app.put("/tasks/{task_id}")
def update_task(task_id:int,updated_task:Task,current_user:str=Depends(get_current_user)):
    db=SessionLocal()
    task=db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if not task:
        return {"error":"No task found"}
    
    task.title = updated_task.title
    task.name = updated_task.name
    task.completed = updated_task.completed

    db.commit()
    db.refresh(task)

    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int,current_user:str=Depends(get_current_user)):
    db = SessionLocal()

    task = db.query(TaskDB).filter(TaskDB.id == task_id).first()

    if not task:
        return {"error": "Task not found"}

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}


@app.post("/register")
def register(user:User):
    db=SessionLocal()

    existing_user=db.query(UserDB).filter(UserDB.email == user.email).first()

    if existing_user:
        return {"Error":"Email already existing"}
    
    hashed_pwd=hash_password(user.password)

    new_user=UserDB(
        email=user.email,
        password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db=SessionLocal()

    db_user=db.query(UserDB).filter(UserDB.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=404,detail="User not found in DB")
    
    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401,detail="Invalid password")
    
    access_token=create_access_token(data={"sub":db_user.email})

    return {
    "access_token": access_token,
    "token_type": "bearer"
            }










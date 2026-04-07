from passlib.context import CryptContext
from jose import JWTError,jwt
from datetime import datetime,timedelta
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from database import SessionLocal
from models import UserDB
from dotenv import load_dotenv
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

oauth2_schema=OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data:dict):
    to_encode=data.copy()
    exp_time=datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":exp_time})
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def get_current_user(token:str = Depends(oauth2_schema)):
    db=SessionLocal()
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        email=payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401,detail="Invalid token")
        
        user=db.query(UserDB).filter(UserDB.email == email).first()

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except JWTError:
        raise HTTPException(status_code=401,detail="Invalid token")
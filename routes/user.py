from fastapi import APIRouter, Depends, HTTPException
from database import SessionLocal
from models import UserDB
from schemas import User
from core.security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/register")
def register(user: User):
    db = SessionLocal()

    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()

    if existing_user:
        return {"Error": "Email already existing"}
    
    new_user = UserDB(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()

    db_user = db.query(UserDB).filter(UserDB.email == form_data.username).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(data={"sub": db_user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
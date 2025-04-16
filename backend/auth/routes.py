from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database.models import User
from database import schemas, database
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from database.database import get_db
from . import auth_handler

router  = APIRouter()

@router.post("/register", response_model=schemas.ShowUser)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pwd = auth_handler.hash_password(user.password)
    new_user = User(username=user.username, email=user.email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == form_data.username).first()
    if not db_user or not auth_handler.verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = auth_handler.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


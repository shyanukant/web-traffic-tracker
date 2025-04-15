from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from jose import JWSError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os


load_dotenv()

# load secret
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain:str, hash:str) -> bool:
    return pwd_context.verify(plain, hash)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
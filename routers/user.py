from fastapi import APIRouter, Depends, HTTPException, status
from models import users
from sqlalchemy.orm import Session
from database import session
from typing import Annotated
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oaut2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

SECRET_KEY = '668f3c8d2f50b3708e8d887a5e3f42c680435ac641eaa3e82b7dbf7e64716c3b'
ALGORITHM = 'HS256'

@router.get('/')
async def temp():
    return {"message" : "hello"}

def get_data():
    db = session()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_data)]

class UserRequests(BaseModel):
    username : str
    password : str
    email : str
    firstname : str
    lastname : str
    role : str

class Token(BaseModel) :
    access_token : str
    token_type : str

def authenticate_user(username : str, password : str, db):
    user = db.query(users).filter(users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_user(Username : str, user_id : int, expires_delta : timedelta) :
    encode = {'sub' : Username, 'id' : user_id}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp' : expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_curr_user(token : Annotated[str, Depends(oaut2_bearer)]) :
    try :
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username : str = payload.get('sub')
        user_id : int = payload.get('id')
        if username is None or user_id is None :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Username / User ID is invalid')
        return {'username' : username, 'user_ID' : user_id}
    except JWTError :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Username / User ID is invalid')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def user_create(user_request : UserRequests, db : db_dependency) :
    user_model = users(
        username = user_request.username,
        password = bcrypt_context.hash(user_request.password),
        email = user_request.email,
        firstname = user_request.firstname,
        lastname = user_request.lastname,
        role = user_request.role,
        is_active = True
    )
    db.add(user_model)
    db.commit()

@router.post("/token", response_model=None)
async def login_access(form_data : Annotated[OAuth2PasswordRequestForm, Depends()], db : db_dependency) -> Token :
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user :
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username / Password is not found !!!")
    token = create_user(user.username, user.id, timedelta(minutes=10))
    return {"access_token" : token, "type" : "bearer"}


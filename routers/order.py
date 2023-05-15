from fastapi import APIRouter, Depends, status, Path, HTTPException
from .user import get_curr_user
from pydantic import BaseModel
from database import session
from typing import Annotated
from sqlalchemy.orm import Session
from models import orders

router = APIRouter(
    prefix='/order',
    tags=['order']
)

@router.get('/')
async def temp():
    return {"message" : "hello"}

class Order(BaseModel):
    item : str
    quantity : int
    pizza_size : str
    flavor : str

class ChangeStatus(BaseModel):
    status : str

def get_data():
    db = session()
    try :
        yield db
    finally:
        db.close()

db_depend = Annotated[Session, Depends(get_data)]
user_depend = Annotated[dict, Depends(get_curr_user)]


@router.get("/items")
async def get_all_user_items(user: user_depend, db: db_depend) :
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication !!!" )
    if user.get('role') != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this data")
    return db.query(orders).filter(orders.owner_id == user.get('user_ID')).all()

@router.post("/generate_order", status_code=status.HTTP_201_CREATED)
async def generate_order(user: user_depend, db : db_depend, order_request : Order) :
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication !!!" )
    if user.get('role') != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this data")
    order_model = orders(**order_request.dict(), order_status="PENDING", costs=order_request.quantity * 150, owner_id=user.get('user_ID'))
    db.add(order_model)
    db.commit()

@router.put("/update_status/{user_id}/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_status(db : db_depend, user : user_depend, order_status : ChangeStatus, user_id : int = Path(gt=0), order_id : int = Path(gt=0)) :
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication !!!" )
    if user.get('role') != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot update this data")
    order_model = db.query(orders).filter(orders.id == order_id).filter(orders.owner_id == user_id).first()
    if order_model is None :
        raise HTTPException(status_code=404, detail='The data you want is not found')
    order_model.order_status = order_status.status
    db.add(order_model)
    db.commit()

@router.delete("/delete_order/{order_id}", status_code=status.HTTP_204_NO_CONTENT) 
async def delete_status(db : db_depend, user : user_depend, order_id : int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Failed Authentication !!!")
    if user.get('role') != "customer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot delete this data")
    order_model = db.query(orders).filter(orders.id == order_id).filter(orders.owner_id == user.get('user_ID')).first()
    if order_model is None:
        raise HTTPException(status_code=404, detail='The data you want is not found')
    db.query(orders).filter(orders.id == order_id).filter(orders.owner_id == user.get('user_ID')).delete()
    db.commit()

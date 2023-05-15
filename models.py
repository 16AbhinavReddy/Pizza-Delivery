from database import base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy_utils.types import ChoiceType

class users(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String, unique=True)
    email = Column(String, unique=True)
    firstname = Column(String)
    lastname = Column(String)
    role = Column(String)
    is_active = Column(Boolean, default=False)

class orders(base):
    __tablename__ = 'orders'
    

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)
    quantity = Column(Integer)
    order_status = Column(String)
    pizza_size = Column(String)
    flavor = Column(String)
    costs = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    

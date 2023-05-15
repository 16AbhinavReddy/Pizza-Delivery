from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

database_url = "sqlite:///./data.db"

engine = create_engine(database_url, connect_args={"check_same_thread" : False})
session = sessionmaker(autoflush=False, autocommit= False, bind=engine)
base = declarative_base()
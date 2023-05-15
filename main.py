from fastapi import FastAPI
from routers import user,order
from database import engine
import models


app = FastAPI()
models.base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(order.router)
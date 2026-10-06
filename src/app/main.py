from fastapi import FastAPI

from src.app import models
from src.app.database import engine, Base
from src.app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
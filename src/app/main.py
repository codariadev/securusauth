from fastapi import FastAPI

from src.app.database import Base, engine
from src.app.routers import auth

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)

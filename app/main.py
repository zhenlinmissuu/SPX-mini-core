from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from routers import users

import models, schemas
from database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(users.router)
app.include_router(users.router)
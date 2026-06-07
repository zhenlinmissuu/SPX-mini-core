from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import models, schemas
from database import AsyncSessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        db.close()




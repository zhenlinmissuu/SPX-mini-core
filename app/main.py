from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import database
from routers import users, orders, events, trips

import models, schemas
from database import SessionLocal, engine

from services.order_service import load_distance

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    load_distance()

app.include_router(users.router)
app.include_router(orders.router)
app.include_router(events.router)
app.include_router(trips.router)

import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from datetime import datetime
import uuid
from models import OrderStatus, TripStatus, TripType, LoadStatus
from database import get_db

router = APIRouter(
    prefix="/trips",
    tags=["trips"]
)

@router.post("/", response_model=schemas.TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(trip: schemas.TripCreate, db: Session = Depends(get_db)):
    try:
        new_trip = models.trips(
            trip_number=f"TRIP-{uuid.uuid4().hex[:6].upper()}",
            type=trip.type,
            status=trip.status,
            start_time=datetime.now(),
            vehicle_id=trip.vehicle_id,
            driver_id=trip.driver_id
        )
        db.add(new_trip)
        db.commit()
        db.refresh(new_trip)

        for idx, o_id in enumerate(trip.order_ids):
            detail = models.trips_detail(
                trip_id=new_trip.trip_id,
                order_id=o_id,
                sequence=idx + 1,
                status=models.LoadStatus.LOADED,
                note="Auto"
            )
            db.add(detail)
        
        if trip.order_ids:
            db.query(models.orders).filter(models.orders.order_id.in_(trip.order_ids)).update(
                {"status": "delivering"}, synchronize_session=False
            )
        
        db.commit()
        return schemas.TripResponse(
            trip_id = new_trip.trip_id,
            trip_number = new_trip.trip_number,
            type = new_trip.type,
            status = new_trip.status,
            order_ids = trip.order_ids,
            vehicle_id = new_trip.vehicle_id,
            driver_id = new_trip.driver_id
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý DB: {str(e)}")

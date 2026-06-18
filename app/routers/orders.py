import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from models import OrderStatus
from services.order_service import shipment_fee
from database import get_db

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate,db: Session = Depends(get_db)):
    fee = shipment_fee(
        sender_province_id = order.sender_province_id, 
        receiver_province_id = order.receiver_province_id, 
        weight = order.weight)
    new_order = models.orders(**order.model_dump())
    
    s_dist =  db.query(models.hubs).filter(models.hubs.district_id == order.sender_district_id).first()
    r_dist = db.query(models.hubs).filter(models.hubs.district_id == order.receiver_district_id).first()

    if not s_dist or not r_dist:
        raise HTTPException(status_code=400, detail="Quận huyện không hợp lệ")
    
    new_order = models.orders(
        **order.model_dump(),
        fee=fee,
        origin_hub_id=s_dist.hub_id,
        destination_hub_id=r_dist.hub_id,
        status=OrderStatus.PENDING,
    )
    
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("/", response_model=list[schemas.OrderResponse])
def get_orders (db: Session = Depends(get_db)):
    return db.query(models.orders).all()

@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order (order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.orders).filter(models.orders.order_id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Không tìm thấy order với id: {order_id}")
    
    return order

@router.put("/{order_id}", response_model=schemas.OrderResponse)
def update_order (order_id: int, order_update: schemas.OrderUpdate, db: Session = Depends(get_db)):
    order = db.query(models.orders).filter(models.orders.order_id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND, 
            detail = f"Không tìm thấy order với id: {order_id}")
    
    update_data = order_update.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        setattr(order, key, value)
    
    db.commit()
    db.refresh(order)

    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order (order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.orders).filter(models.orders.order_id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Không tìm thấy đơn hàng với mã vận đơn {order_id}"
        )

    db.delete(order)
    db.commit()

    return None
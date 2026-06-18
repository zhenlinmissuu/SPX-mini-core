import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from models import OrderStatus
from services.order_service import STATUS_TRANSITIONS
from database import get_db

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.post("/scan")
def scan_order_event(order_id: int, next_status: str, db: Session = Depends(get_db)):
    order = db.query(models.orders).filter(models.orders.order_id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    current_status_str = order.status.value
    allowed_statuses = STATUS_TRANSITIONS.get(current_status_str, [])

    if next_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    order.status = OrderStatus(next_status)
    db.commit()
    db.refresh(order)
    
    return {"message": "Order status updated successfully", "new_status": order.status}

@router.post("/scan-home")
def scan_at_home(order_id: int, outcome: str, db: Session = Depends(get_db)):
    from datetime import datetime
    if outcome not in ["delivered", "cancelled"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Kết quả quét tại nhà không hợp lệ")
    
    order = db.query(models.orders).filter(models.orders.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy đơn hàng")
    
    if order.status != models.OrderStatus.DELIVERING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Không thể chốt vì trạng thái đơn hàng đang là {order.status}")
    
    try:
        # Cập nhật trạng thái đơn hàng
        order.status = models.OrderStatus(outcome)
        
        # Đồng thời cập nhật trạng thái trong chi tiết chuyến đi (trips_detail)
        detail = db.query(models.trips_detail).filter(models.trips_detail.order_id == order_id).first()
        if detail:
            detail.status = models.LoadStatus(outcome)
            db.flush()
            
            # Kiểm tra xem toàn bộ các đơn hàng trong chuyến này đã hoàn thành chưa (không còn trạng thái LOADED)
            trip_id = detail.trip_id
            unfinished = db.query(models.trips_detail).filter(
                models.trips_detail.trip_id == trip_id,
                models.trips_detail.status == models.LoadStatus.LOADED
            ).all()
            
            # Nếu tất cả đã được giao hoặc hủy, cập nhật trạng thái chuyến đi thành COMPLETED
            if len(unfinished) == 0:
                trip = db.query(models.trips).filter(models.trips.trip_id == trip_id).first()
                if trip:
                    trip.status = models.TripStatus.COMPLETED
                    trip.arrived_time = datetime.now()
        
        db.commit()
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Lỗi xử lý Database: {str(e)}")
    
    return {
        "message": "Cập nhật trạng thái đơn hàng thành công",
        "order_id": order.order_id,
        "final_status": order.status
    }
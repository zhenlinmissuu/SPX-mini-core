from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum as PyEnum

#User
class UserRole(str, PyEnum):
    ADMIN = "admin"
    STAFF = "staff"
    CLIENT = "client"

class UserBase(BaseModel):
    user_name: str = Field(..., max_length=50, description="Tên người dùng")
    user_phone: str = Field(..., 
                            min_length=9, 
                            max_length=11, 
                            pattern = r'^0\d{8,10}$',
                            description="Số điện thoại người dùng")
    user_role: UserRole = Field(default=UserRole.CLIENT, description="Vai trò trong hệ thống")

class UserCreate(UserBase):
    password: str = Field(..., max_length=255, description="Mật khẩu thô của người dùng")

class UserResponse(UserBase):
    user_id: int = Field(..., description="ID của người dùng")

    class Config:
        from_attributes = True

# Miscellaneous
class ProvinceBase(BaseModel):
    province_name: str = Field(..., max_length=50)

class ProvinceResponse(ProvinceBase):
    province_id: int

    class Config:
        from_attributes = True

class DistrictBase(BaseModel):
    district_name: str = Field(..., max_length=50)
    province_name: str = Field(..., max_length=50)

class DistrictResponse(DistrictBase):
    district_id: int
    province_id: int

    class Config:
        from_attributes = True

class VehicleBase(BaseModel):
    vehicle_name: str = Field(..., max_length=50, description="Tên phương tiện")

class VehicleResponse(VehicleBase):
    vehicle_id: int = Field(..., description="ID của phương tiện")
    vehicle_plate: str = Field(..., max_length=10, description="Biển số phương tiện")
    hub_id: int = Field(..., description="ID kho quản lý xe")

    class Config:
        from_attributes = True
    
#Hubs
class HubStatus(str, PyEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

class HubBase(BaseModel):
    hub_name: str = Field(..., max_length=50, description="Tên kho")
    hub_address: str = Field(..., max_length=100, description="Địa chỉ kho")
    hub_status: HubStatus = Field(default=HubStatus.ACTIVE, description="Trạng thái kho")

    province_id: int = Field(..., description="ID của tỉnh")
    district_id: int = Field(..., description="ID của quận/huyện")

class HubCreate(HubBase):
    pass

class HubResponse(HubBase):
    hub_id: int = Field(..., description='ID của kho')
    province_detail: Optional[ProvinceResponse] = None
    district_detail: Optional[DistrictResponse] = None

    class Config:
        from_attributes = True

#Orders
class OrderStatus(str, PyEnum):
    PENDING = 'pending'
    COLLECTED = 'collected'
    IN_TRANSIT = 'in_transit'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    RETURNING = 'returning'
    RETURNED = 'returned'
    
class OrderBase(BaseModel):
    receiver_name: str = Field(..., max_length=50, description="Tên người nhận")
    receiver_phone: str = Field(..., max_length=11, description="Số điện thoại người nhận")
    receiver_address: str = Field(..., max_length=100, description="Địa chỉ người nhận")
    province_name: str = Field(..., max_length=50, description="Tên tỉnh")
    district_name: str = Field(..., max_length=50, description="Tên quận/huyện")
    weight: int = Field(..., description="Trọng lượng đơn hàng")
    cod: int = Field(..., description="Tiền COD")
    origin_hub_id: int = Field(..., description="ID kho xuất phát")
    created_at = datetime.now()

class OrderCreate(OrderBase):
    pass
class OrderResponse(OrderBase):
    order_id: int = Field(..., description="ID của đơn hàng")
    tracking_number: str = Field(..., max_length=20, description="Số vận đơn")
    fee: int = Field(..., description="Phí vận chuyển")
    status: OrderStatus = Field(..., description="Trạng thái đơn hàng")
    destination_hub_id: int = Field(..., description="ID kho đích")

    class Config:
        from_attributes = True

#Trips
class TripStatus(str, PyEnum):
    PLANNED = 'planned'
    DEPARTED = 'departed'
    ARRIVED = 'arrived'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class TripType(str, PyEnum):
    INTER_HUB = 'inter_hub'
    PICKUP = 'pickup'
    DELIVERY = 'delivery'

class TripBase(BaseModel):
    type: TripType = Field(..., description="Loại chuyến đi")
    status: TripStatus = Field(..., description="Trạng thái chuyến đi")
    vehicle_id: int = Field(..., description="ID của phương tiện")
    driver_id: int = Field(..., description="ID của tài xế")

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    trip_id: int = Field(..., description="ID của chuyến đi")
    trip_number: str = Field(..., max_length=20, description="Số chuyến đi")

class LoadStatus: 
    LOADED = 'loaded'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class TripDetailBase(BaseModel):
    note: Optional[str] = Field(None, max_length=255, description="Ghi chú")

class TripDetailCreate(TripDetailBase):
    sequence: Optional[int] = Field(None, description="Thứ tự giao")
    order_id: int = Field(..., description="ID của đơn hàng")

class TripDetailUpdate(TripDetailBase):
    status: LoadStatus = Field(..., description="Cập nhật trạng thái giao hàng")
    sequence: Optional[int] = Field(None, description="Cho phép đổi thứ tự giao")

class TripDetailResponse(TripDetailBase):
    trip_log_id: int = Field(..., description="ID của bản ghi")
    trip_id: int = Field(..., description="ID của chuyến đi")
    order_id: int = Field(..., description="ID của đơn hàng")
    status: LoadStatus = Field(..., description="Trạng thái giao hàng")
    sequence: Optional[int] = Field(..., description="Thứ tự giao")

    class Config:
        from_attributes = True

class OrderTrackingLogBase(BaseModel):
    description: str = Field(..., max_length=255, description="Mô tả")

class OrderTrackingLogCreate(OrderTrackingLogBase):
    order_id: str = Field(..., description="ID của đơn hàng")
    hub_id: str = Field(..., description="ID của kho")
    status: OrderStatus = Field(..., description="Trạng thái đơn hàng")

class OrderTrackingLogResponse(OrderTrackingLogBase):
    order_log_id: int = Field(..., description="ID của bản ghi")
    order_id: int = Field(..., description="ID của đơn hàng")
    hub_id: int = Field(..., description="ID của kho")
    status: OrderStatus = Field(..., description="Trạng thái đơn hàng")
    created_at: datetime = Field(..., description="Thời gian tạo bản ghi")

    class Config:
        from_attributes = True

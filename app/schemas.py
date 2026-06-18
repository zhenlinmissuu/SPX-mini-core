from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from models import TripStatus, TripType, UserRole, HubStatus, OrderStatus
from enum import Enum as PyEnum

#User
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

class UserUpdate(BaseModel):
    user_name: Optional[str] = Field(None, max_length=50, description="Tên người dùng")
    user_phone: Optional[str] = Field(None, 
                            min_length=9, 
                            max_length=11, 
                            pattern = r'^0\d{8,10}$',
                            description="Số điện thoại người dùng")
    user_role: Optional[UserRole] = Field(default=UserRole.CLIENT, description="Vai trò trong hệ thống")

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
class OrderBase(BaseModel):
    sender_name: str = Field(..., max_length=50, description="Tên người gửi")
    sender_phone: str = Field(..., max_length=11, description="Số điện thoại người gửi")
    sender_address: str = Field(..., max_length=100, description="Địa chỉ người gửi")

    receiver_name: str = Field(..., max_length=50, description="Tên người nhận")
    receiver_phone: str = Field(..., max_length=11, description="Số điện thoại người nhận")
    receiver_address: str = Field(..., max_length=100, description="Địa chỉ người nhận")
    
    sender_district_id: int = Field(..., description="ID huyện người gửi")
    sender_province_id: int = Field(..., description="ID tỉnh người gửi")
    receiver_province_id: int = Field(..., description="ID tỉnh người nhận")
    receiver_district_id: int = Field(..., description="ID huyện người nhận")
    
    weight: int = Field(..., description="Trọng lượng đơn hàng")
    cod: int = Field(..., description="Tiền COD")
    created_at: datetime = Field(default_factory=datetime.now)


class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    sender_name: Optional[str] = Field(None, max_length=50, description="Tên người gửi")
    sender_phone: Optional[str] = Field(None, max_length=11, description="Số điện thoại người gửi")
    sender_address: Optional[str] = Field(None, max_length=100, description="Địa chỉ người gửi")
    receiver_name: Optional[str] = Field(None, max_length=50, description="Tên người nhận")
    receiver_phone: Optional[str] = Field(None, max_length=11, description="Số điện thoại người nhận")
    receiver_address: Optional[str] = Field(None, max_length=100, description="Địa chỉ người nhận")
    
    sender_district_id: Optional[int] = Field(None, description="ID huyện người gửi")
    sender_province_id: Optional[int] = Field(None, description="ID tỉnh người gửi")
    receiver_province_id: Optional[int] = Field(None, description="ID tỉnh người nhận")
    receiver_district_id: Optional[int] = Field(None, description="ID huyện người nhận")
    
    weight: Optional[int] = Field(None, description="Trọng lượng đơn hàng")
    cod: Optional[int] = Field(None, description="Tiền COD")
    origin_hub_id: Optional[int] = Field(None, description="ID kho xuất phát")


class OrderResponse(OrderBase):
    order_id: int = Field(..., description="ID của đơn hàng")
    fee: int = Field(..., description="Phí vận chuyển")
    status: OrderStatus = Field(..., description="Trạng thái đơn hàng")
    origin_hub_id: int = Field(...)
    destination_hub_id: int = Field(..., description="ID kho đích")
    trip_id: Optional[int] = Field(None, description="ID chuyến đi")

    class Config:
        from_attributes = True

#Trips
class TripBase(BaseModel):
    type: TripType = Field(..., description="Loại chuyến đi")
    status: TripStatus = Field(..., description="Trạng thái chuyến đi")
    order_ids: List[int] = Field([], description="ID của đơn hàng")
    vehicle_id: int = Field(..., description="ID của phương tiện")
    driver_id: int = Field(..., description="ID của tài xế")

class TripCreate(TripBase):
    pass

class TripResponse(TripBase):
    trip_id: int = Field(..., description="ID của chuyến đi")
    trip_number: str = Field(..., max_length=20, description="Số chuyến đi")

class LoadStatus(str, PyEnum): 
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

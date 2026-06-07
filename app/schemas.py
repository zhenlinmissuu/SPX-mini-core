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
    user_phone: str = Field(..., max_length=11, description="Số điện thoại người dùng")
    user_role: UserRole = Field(default=UserRole.CLIENT, description="Vai trò trong hệ thống")

    @field_validator('user_phone')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        if not (9 <= len(v) <= 11):
            raise ValueError('Số điện thoại không hợp lệ')
        return v
    
class UserCreate(UserBase):
    password: str = Field(..., max_length=255, description="Mật khẩu thô của người dùng")

class UserResponse(UserBase):
    user_id: int = Field(..., description="ID của người dùng")

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
    tracking_number: str = Field(..., max_length=20, description="Số vận đơn")
    receiver_name: str = Field(..., max_length=50, description="Tên người nhận")
    receiver_phone: str = Field(..., max_length=11, description="Số điện thoại người nhận")
    receiver_address: str = Field(..., max_length=100, description="Địa chỉ người nhận")
    weight: int = Field(..., description="Trọng lượng đơn hàng")
    cod: int = Field(..., description="Tiền COD")
    created_at = datetime.now()
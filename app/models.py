from datetime import datetime
from database import Base
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Integer, DateTime, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#Base
class Base(DeclarativeBase):
    pass

#Users
class UserRole(str, PyEnum):
    ADMIN = "admin"
    STAFF = "staff"
    CLIENT = "client"

class user(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_phone: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    user_role: Mapped[UserRole] = mapped_column(String(10), nullable=False)

#Hubs
class HubStatus(str, PyEnum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'

class hubs(Base):
    __tablename__ = 'hubs'

    hub_id: Mapped[int] = mapped_column(primary_key=True)
    hub_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hub_address: Mapped[str] = mapped_column(String(100), nullable=False)
    hub_status: Mapped[HubStatus] = mapped_column(String(10), nullable=False)

    #Foreign Keys
    province_id: Mapped[int] = mapped_column(ForeignKey('provinces.province_id'))
    district_id: Mapped[int] = mapped_column(ForeignKey('districts.district_id'))

#Orders
class OrderStatus(str, PyEnum):
    PICKED_UP = 'picked_up'
    PENDING = 'pending'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class orders(Base):
    __tablename__ = 'orders'

    order_id: Mapped[int] = mapped_column(primary_key=True)

    sender_name: Mapped[str] = mapped_column(String(50), nullable=False)
    sender_phone: Mapped[str] = mapped_column(String(11), nullable=False)
    sender_address: Mapped[str] = mapped_column(String(100), nullable=False)

    receiver_name: Mapped[str] = mapped_column(String(50), nullable=False)
    receiver_phone: Mapped[str] = mapped_column(String(11), nullable=False)
    receiver_address: Mapped[str] = mapped_column(String(100), nullable=False)

    weight: Mapped[int] = mapped_column(Integer, nullable=False) #grams
    cod: Mapped[int] = mapped_column(Integer, nullable=False) #Vnd
    fee: Mapped[int] = mapped_column(Integer, nullable=False) #Vnd
    status: Mapped[OrderStatus] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())



    #Foreign Keys
    origin_hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))
    destination_hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))

    sender_province_id: Mapped[int] = mapped_column(ForeignKey('provinces.province_id'))
    sender_district_id: Mapped[int] = mapped_column(ForeignKey('districts.district_id'))
    receiver_province_id: Mapped[int] = mapped_column(ForeignKey('provinces.province_id'))
    receiver_district_id: Mapped[int] = mapped_column(ForeignKey('districts.district_id'))

    trip_id: Mapped[int] = mapped_column(ForeignKey('trips.trip_id'), nullable=True)

#Trips
class TripStatus(str, PyEnum):
    ONGOING = 'ongoing'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class TripType(str, PyEnum):
    INTER_HUB = 'inter_hub'
    PICKUP = 'pickup'
    DELIVERY = 'delivery'

class LoadStatus(str, PyEnum): 
    LOADED = 'loaded'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class trips(Base):
    __tablename__ = 'trips'

    trip_id: Mapped[int] = mapped_column(primary_key=True)
    trip_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    type: Mapped[TripType] = mapped_column(String(20), nullable=False)
    status: Mapped[TripStatus] = mapped_column(String(10), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arrived_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), default=None, nullable=True)
    
    
    #Foreign Keys
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicles.vehicle_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))

class trips_detail(Base):
    __tablename__ = 'trips_detail'

    trip_log_id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey('trips.trip_id'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id'), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[LoadStatus] = mapped_column(String(10), nullable=False)
    note: Mapped[str] = mapped_column(String(255), nullable=False)

class order_tracking_logs(Base):
    __tablename__ = 'order_tracking_logs'

    order_log_id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus] = mapped_column(String(10), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    #Foreign Keys
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.order_id'))
    hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))


#Miscellaneous
class provinces(Base):
    __tablename__ = 'provinces'

    province_id: Mapped[int] = mapped_column(primary_key=True)
    province_name: Mapped[str] = mapped_column(String(50), nullable=False)


class districts(Base):
    __tablename__ = 'districts'

    district_id: Mapped[int] = mapped_column(primary_key=True)
    district_name: Mapped[str] = mapped_column(String(50), nullable=False)
    province_id: Mapped[int] = mapped_column(ForeignKey('provinces.province_id'))

class Vehicles(Base):
    __tablename__ = 'vehicles'

    vehicle_id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_name: Mapped[str] = mapped_column(String(50), nullable=False)
    plate_number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    #Foreign Keys
    hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))
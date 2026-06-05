from datetime import datetime
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
    user_phone: Mapped[str] = mapped_column(String(11), unique=True)
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

#Oders
class OderStatus(str, PyEnum):
    PENDING = 'pending'
    COLLECTED = 'collected'
    IN_TRANSIT = 'in_transit'
    DELIVERING = 'delivering'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'
    RETURNING = 'returning'
    RETURNED = 'returned'

class oders(Base):
    order_id: Mapped[int] = mapped_column(primary_key=True)
    tracking_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    receiver_name: Mapped[str] = mapped_column(String(50), nullable=False)
    receiver_phone: Mapped[str] = mapped_column(String(11), nullable=False)
    recerver_address: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False) #grams
    cod: Mapped[int] = mapped_column(Integer, nullable=False) #Vnd
    fee: Mapped[int] = mapped_column(Integer, nullable=False) #Vnd
    status: Mapped[OderStatus] = mapped_column(String(10), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())



    #Foreign Keys
    origin_hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))
    destination_hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))
    province_id: Mapped[int] = mapped_column(ForeignKey('provinces.province_id'))
    district_id: Mapped[int] = mapped_column(ForeignKey('districts.district_id'))

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

class trips(Base):
    trip_id: Mapped[int] = mapped_column(primary_key=True)
    trip_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    type: Mapped[TripType] = mapped_column(String(10), nullable=False)
    status: Mapped[TripStatus] = mapped_column(String(10), nullable=False)

    
    #Foreign Keys
    oder_id: Mapped[int] = mapped_column(ForeignKey('oders.order_id'))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicles.vehicle_id'))
    driver_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))

class LoadStatus: 
    LOADED = 'loaded'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class trips_detail(Base):
    trip_id: Mapped[int] = mapped_column(ForeignKey('trips.trip_id'), primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('oders.order_id'), primary_key=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[LoadStatus] = mapped_column(String(10), nullable=False)


#Miscellaneous
class provinces(Base):
    __tablename__ = 'provinces'

    province_id: Mapped[int] = mapped_column(primary_key=True)

class districts(Base):
    __tablename__ = 'districts'

    district_id: Mapped[int] = mapped_column(primary_key=True)

class Vehicles(Base):
    vehicle_id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_name: Mapped[str] = mapped_column(String(50), nullable=False)
    plate_number: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    #Foreign Keys
    hub_id: Mapped[int] = mapped_column(ForeignKey('hubs.hub_id'))
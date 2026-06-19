import os
import sys
import random
import time
from datetime import datetime
from tqdm import tqdm
from faker import Faker
from sqlalchemy.orm import Session

# Thêm đường dẫn app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, Base, engine
from app import models
from app.data_seed import seed_data
from app.services.order_service import load_distance, shipment_fee

fake = Faker('vi_VN')

def generate_random_orders(db: Session, num_orders: int = 50000):
    print(f"\n🚀 Bắt đầu tạo {num_orders} đơn hàng...")
    start_time = time.time()
    
    # Lấy dữ liệu cơ sở
    districts = db.query(models.districts).all()
    hubs = {h.district_id: h.hub_id for h in db.query(models.hubs).all()}
    
    if not districts or not hubs:
        print("❌ Chưa có dữ liệu quận/huyện và Hub. Đang seed dữ liệu cơ sở...")
        seed_data(db)
        districts = db.query(models.districts).all()
        hubs = {h.district_id: h.hub_id for h in db.query(models.hubs).all()}

    load_distance()
    
    orders_to_insert = []
    
    print("⏳ Đang xử lý data trên RAM...")
    for _ in tqdm(range(num_orders), desc="Generating Orders"):
        s_dist = random.choice(districts)
        r_dist = random.choice(districts)
        
        # Nếu chưa có hub thì bỏ qua hoặc chọn lại, nhưng vì đã seed nên chắc chắn có hub
        s_hub_id = hubs.get(s_dist.district_id)
        r_hub_id = hubs.get(r_dist.district_id)
        
        if not s_hub_id or not r_hub_id:
            continue
            
        weight = random.randint(100, 50000) # 100g -> 50kg
        fee = shipment_fee(s_dist.province_id, r_dist.province_id, weight)
        
        orders_to_insert.append(models.orders(
            sender_name=fake.name(),
            sender_phone=fake.phone_number()[:11],
            sender_address=fake.street_address(),
            receiver_name=fake.name(),
            receiver_phone=fake.phone_number()[:11],
            receiver_address=fake.street_address(),
            weight=weight,
            cod=random.randint(0, 5000) * 1000,
            fee=fee,
            status=models.OrderStatus.PENDING,
            origin_hub_id=s_hub_id,
            destination_hub_id=r_hub_id,
            sender_province_id=s_dist.province_id,
            sender_district_id=s_dist.district_id,
            receiver_province_id=r_dist.province_id,
            receiver_district_id=r_dist.district_id
        ))

    print(f"⏳ Đang đẩy {len(orders_to_insert)} đơn hàng vào Database (Bulk Insert)...")
    
    # Bulk insert (Rất nhanh, chỉ vài giây cho 50k bản ghi)
    db.bulk_save_objects(orders_to_insert)
    db.commit()
    
    elapsed = time.time() - start_time
    print(f"✅ Đã tạo xong {len(orders_to_insert)} đơn hàng trong {elapsed:.2f} giây.")
    
    return [o.order_id for o in db.query(models.orders.order_id).limit(len(orders_to_insert)).all()]

def generate_trips(db: Session, order_ids: list):
    print("\n🚚 Đang gom các đơn hàng thành các chuyến đi (Trips)...")
    start_time = time.time()
    
    vehicles = db.query(models.Vehicles).all()
    drivers = db.query(models.user).filter(models.user.user_role == models.UserRole.STAFF).all()
    
    if not vehicles or not drivers:
        print("❌ Thiếu dữ liệu xe hoặc tài xế.")
        return

    # Giả sử 1 chuyến xe chở tối đa 100 đơn hàng
    batch_size = 100
    trips_to_insert = []
    
    # Đọc max_trip_id để tự tính trip_id (dùng cho bulk_save trips_detail)
    # Tuy nhiên bulk_save không trả về ID. 
    # Do đó với các luồng phức tạp như Trip/Detail ta sẽ dùng add_all và flush.
    trip_details_to_insert = []
    
    print("⏳ Tạo Trips...")
    # Lấy các orders thực sự
    orders = db.query(models.orders).filter(models.orders.order_id.in_(order_ids)).all()
    
    trips_objects = []
    for i in tqdm(range(0, len(orders), batch_size), desc="Grouping Trips"):
        batch_orders = orders[i:i+batch_size]
        vehicle = random.choice(vehicles)
        driver = random.choice(drivers)
        
        trip = models.trips(
            trip_number=f"TRIP-{fake.bothify(text='????##').upper()}",
            type=models.TripType.DELIVERY,
            status=models.TripStatus.ONGOING,
            start_time=datetime.now(),
            vehicle_id=vehicle.vehicle_id,
            driver_id=driver.user_id
        )
        trips_objects.append((trip, batch_orders))

    # Save trips to get IDs
    for trip, _ in trips_objects:
        db.add(trip)
    db.commit()

    print("⏳ Cập nhật trạng thái Order và tạo Trips Detail...")
    for trip, batch_orders in tqdm(trips_objects, desc="Mapping Details"):
        for idx, order in enumerate(batch_orders):
            trip_details_to_insert.append(models.trips_detail(
                trip_id=trip.trip_id,
                order_id=order.order_id,
                sequence=idx + 1,
                status=models.LoadStatus.LOADED,
                note="Auto generated performance test"
            ))
            order.status = models.OrderStatus.DELIVERING
            order.trip_id = trip.trip_id

    db.bulk_save_objects(trip_details_to_insert)
    db.commit()
    
    elapsed = time.time() - start_time
    print(f"✅ Đã tạo xong {len(trips_objects)} chuyến đi trong {elapsed:.2f} giây.")
    
    return trips_objects

def complete_trips(db: Session, trips_objects: list):
    print("\n✅ Đang hoàn thành các chuyến đi...")
    start_time = time.time()
    
    for trip, batch_orders in tqdm(trips_objects, desc="Completing Trips"):
        # Chốt đơn hàng
        for order in batch_orders:
            order.status = models.OrderStatus.DELIVERED
            
        # Chốt trip detail
        db.query(models.trips_detail).filter(models.trips_detail.trip_id == trip.trip_id).update(
            {"status": models.LoadStatus.DELIVERED}, synchronize_session=False
        )
        
        # Chốt chuyến đi
        trip.status = models.TripStatus.COMPLETED
        trip.arrived_time = datetime.now()
        
    db.commit()
    elapsed = time.time() - start_time
    print(f"✅ Hoàn thành tất cả các chuyến đi trong {elapsed:.2f} giây.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("⚠️ Làm sạch database trước khi test hiệu năng...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        
        seed_data(db)
        
        # 1. Tạo 50,000 orders
        order_ids = generate_random_orders(db, 50000)
        
        # 2. Gom nhóm orders thành chuyến đi
        trips_objects = generate_trips(db, order_ids)
        
        # 3. Hoàn thành chuyến đi
        complete_trips(db, trips_objects)
        
        print("\\n🎉 PERFORMANCE TEST COMPLETED SUCCESSFULLY!")
    finally:
        db.close()

import pytest
from fastapi.testclient import TestClient
import uuid
import sys
import random
import os

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app
from app.database import Base, engine, SessionLocal
from app.data_seed import seed_data

# Khởi tạo TestClient
client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    # Setup
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_data(db)
    db.close()
    
    yield
    
    # Teardown
    Base.metadata.drop_all(bind=engine)

def test_create_user():
    unique_phone = f"0987{random.randint(100000, 999999)}"
    response = client.post(
        "/users/",
        json={
            "user_name": "Nguyen Van A",
            "user_phone": unique_phone,
            "user_role": "client",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user_phone"] == unique_phone
    assert "user_id" in data

def test_create_order():
    # Cần hub, province, district (đã có từ data_seed)
    response = client.post(
        "/orders/",
        json={
            "sender_name": "Nguyen Van A",
            "sender_phone": "0987654321",
            "sender_address": "123 Xuan Thuy",
            "receiver_name": "Tran Van B",
            "receiver_phone": "0912345678",
            "receiver_address": "456 Le Loi",
            "sender_district_id": 1,
            "sender_province_id": 1,
            "receiver_province_id": 2,
            "receiver_district_id": 15,
            "weight": 1000,
            "cod": 50000
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "order_id" in data
    assert data["status"] == "pending"

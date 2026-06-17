# test_fee.py
from app.services.order_service import load_distance, shipment_fee

# 1. Kích hoạt luồng nạp file JSON lên RAM (FastAPI sẽ làm việc này khi khởi động)
load_distance()

# 2. Chạy thử nghiệm tính phí giữa Tỉnh 1 (Hà Nội) và Tỉnh 2 (Hải Phòng), hàng nặng 1000g (1kg)
# Theo file JSON của bạn: matrix[1][2] = 106.46 km
fee_1_to_2 = shipment_fee(
    sender_province_id=1,
    receiver_province_id=2,
    weight=1000
)

print(f"--> Chi phí tính toán thực tế từ Hà Nội sang Hải Phòng: {fee_1_to_2} VNĐ")
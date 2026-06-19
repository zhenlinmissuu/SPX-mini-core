import json
from pathlib import Path

DISTANCE_MEMORY_CACHE = {}

STATUS_TRANSITIONS = {
    "pending": ["picked_up", "cancelled"],
    "picked_up": ["delivering"],
    "delivering": ["delivered", "cancelled"],
    "delivered": [],
    "cancelled": []
}

def load_distance():
    """
    Nạp dữ liệu ma trận khoảng cách từ file JSON vào RAM khi khởi động Server.
    """
    global DISTANCE_MEMORY_CACHE

    file_path = Path(__file__).parent / "provinces_distance.json"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            DISTANCE_MEMORY_CACHE = {
                int(src): {int(dst): float(km) for dst, km in dst_maps.items()}
                for src, dst_maps in raw_data.items()
            }
        print(f">>> [SUCCESS] Đã nạp thành công ma trận khoảng cách từ: {file_path.name}")
    else:
        print(f">>> [ERROR] Không tìm thấy file tại đường dẫn mong muốn: {file_path.resolve()}")
        print(">>> Tầng tính phí sẽ tạm thời sử dụng giá trị mặc định để tránh sập hệ thống.")

def shipment_fee(
        sender_province_id: int,
        receiver_province_id: int,
        weight: int):

    if sender_province_id == receiver_province_id:
        return 16500

    sender_map = DISTANCE_MEMORY_CACHE.get(sender_province_id,{})

    distance_km = sender_map.get(receiver_province_id, 150)

    cost_rate = 0.3

    fee = weight * cost_rate * distance_km

    final_fee = max(fee, 30000)

    return final_fee
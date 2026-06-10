import random
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import provinces, districts, hubs, Vehicles, HubStatus

def seed_data(db: Session):
    # Danh sách các tỉnh miền Bắc và một số quận/huyện tiêu biểu
    northern_provinces = {
        "Hà Nội": ["Quận Ba Đình", "Quận Hoàn Kiếm", "Quận Tây Hồ", "Quận Long Biên", "Quận Cầu Giấy", "Quận Đống Đa", "Quận Hai Bà Trưng", "Quận Hoàng Mai", "Quận Thanh Xuân", "Huyện Sóc Sơn", "Huyện Đông Anh", "Huyện Gia Lâm", "Huyện Nam Từ Liêm", "Huyện Bắc Từ Liêm"],
        "Hà Giang": ["Thành phố Hà Giang", "Huyện Đồng Văn", "Huyện Mèo Vạc", "Huyện Yên Minh", "Huyện Quản Bạ"],
        "Cao Bằng": ["Thành phố Cao Bằng", "Huyện Bảo Lâm", "Huyện Bảo Lạc", "Huyện Thông Nông", "Huyện Hà Quảng"],
        "Bắc Kạn": ["Thành phố Bắc Kạn", "Huyện Pác Nặm", "Huyện Ba Bể", "Huyện Ngân Sơn", "Huyện Bạch Thông"],
        "Tuyên Quang": ["Thành phố Tuyên Quang", "Huyện Lâm Bình", "Huyện Na Hang", "Huyện Chiêm Hóa", "Huyện Hàm Yên"],
        "Lào Cai": ["Thành phố Lào Cai", "Huyện Bát Xát", "Huyện Mường Khương", "Huyện Si Ma Cai", "Huyện Bắc Hà"],
        "Điện Biên": ["Thành phố Điện Biên Phủ", "Thị xã Mường Lay", "Huyện Mường Nhé", "Huyện Mường Chà", "Huyện Tủa Chùa"],
        "Lai Châu": ["Thành phố Lai Châu", "Huyện Tam Đường", "Huyện Mường Tè", "Huyện Sìn Hồ", "Huyện Phong Thổ"],
        "Sơn La": ["Thành phố Sơn La", "Huyện Quỳnh Nhai", "Huyện Thuận Châu", "Huyện Mường La", "Huyện Bắc Yên"],
        "Yên Bái": ["Thành phố Yên Bái", "Thị xã Nghĩa Lộ", "Huyện Lục Yên", "Huyện Văn Yên", "Huyện Mù Cang Chải"],
        "Hòa Bình": ["Thành phố Hòa Bình", "Huyện Đà Bắc", "Huyện Kỳ Sơn", "Huyện Lương Sơn", "Huyện Kim Bôi"],
        "Thái Nguyên": ["Thành phố Thái Nguyên", "Thành phố Sông Công", "Huyện Định Hóa", "Huyện Phú Lương", "Huyện Đồng Hỷ"],
        "Lạng Sơn": ["Thành phố Lạng Sơn", "Huyện Tràng Định", "Huyện Bình Gia", "Huyện Văn Lãng", "Huyện Cao Lộc"],
        "Quảng Ninh": ["Thành phố Hạ Long", "Thành phố Móng Cái", "Thành phố Cẩm Phả", "Thành phố Uông Bí", "Thị xã Đông Triều", "Thị xã Quảng Yên"],
        "Bắc Giang": ["Thành phố Bắc Giang", "Huyện Yên Thế", "Huyện Tân Yên", "Huyện Lạng Giang", "Huyện Lục Nam"],
        "Phú Thọ": ["Thành phố Việt Trì", "Thị xã Phú Thọ", "Huyện Đoan Hùng", "Huyện Hạ Hòa", "Huyện Thanh Ba"],
        "Vĩnh Phúc": ["Thành phố Vĩnh Yên", "Thành phố Phúc Yên", "Huyện Lập Thạch", "Huyện Tam Dương", "Huyện Tam Đảo"],
        "Bắc Ninh": ["Thành phố Bắc Ninh", "Huyện Yên Phong", "Huyện Quế Võ", "Huyện Tiên Du", "Thị xã Từ Sơn", "Huyện Thuận Thành"],
        "Hải Dương": ["Thành phố Hải Dương", "Thành phố Chí Linh", "Huyện Nam Sách", "Huyện Kinh Môn", "Huyện Kim Thành"],
        "Hải Phòng": ["Quận Hồng Bàng", "Quận Ngô Quyền", "Quận Lê Chân", "Quận Hải An", "Quận Kiến An", "Quận Đồ Sơn", "Quận Dương Kinh", "Huyện Thuỷ Nguyên", "Huyện An Dương", "Huyện An Lão"],
        "Hưng Yên": ["Thành phố Hưng Yên", "Huyện Văn Lâm", "Huyện Văn Giang", "Huyện Yên Mỹ", "Huyện Mỹ Hào"],
        "Thái Bình": ["Thành phố Thái Bình", "Huyện Quỳnh Phụ", "Huyện Hưng Hà", "Huyện Đông Hưng", "Huyện Thái Thụy"],
        "Hà Nam": ["Thành phố Phủ Lý", "Huyện Duy Tiên", "Huyện Kim Bảng", "Huyện Thanh Liêm", "Huyện Bình Lục", "Huyện Lý Nhân"],
        "Nam Định": ["Thành phố Nam Định", "Huyện Mỹ Lộc", "Huyện Vụ Bản", "Huyện Ý Yên", "Huyện Nghĩa Hưng"],
        "Ninh Bình": ["Thành phố Ninh Bình", "Thành phố Tam Điệp", "Huyện Nho Quan", "Huyện Gia Viễn", "Huyện Hoa Lư"]
    }

    # Các dòng xe tải/bán tải phổ biến
    vehicle_models = [
        "Hyundai Porter 150", "Kia K200", "Isuzu QKR", "Hino XZU", 
        "Thaco Towner", "Ford Ranger", "Toyota Hilux", "Mitsubishi Triton", 
        "Suzuki Carry", "Dongben K9", "TATA Super Ace"
    ]

    try:
        # Kiểm tra xem dữ liệu đã được seed chưa
        if db.query(provinces).first():
            print("Database đã có dữ liệu. Bỏ qua quá trình seed.")
            return

        print("Đang tạo dữ liệu Tỉnh/Thành phố và Quận/Huyện...")
        all_districts_db = []
        for prov_name, dist_names in northern_provinces.items():
            new_prov = provinces(province_name=prov_name)
            db.add(new_prov)
            db.flush() # Để lấy province_id ngay lập tức

            for dist_name in dist_names:
                new_dist = districts(district_name=dist_name, province_id=new_prov.province_id)
                db.add(new_dist)
                all_districts_db.append(new_dist)
        
        db.flush() 
        
        print("Đang tạo dữ liệu Hubs...")
        all_hubs_db = []
        for dist in all_districts_db:
            # Đặt tên hub theo tên quận/huyện
            hub_name = f"Hub {dist.district_name}"
            hub_address = f"Trung tâm phân phối {dist.district_name}"
            new_hub = hubs(
                hub_name=hub_name,
                hub_address=hub_address,
                hub_status=HubStatus.ACTIVE,
                province_id=dist.province_id,
                district_id=dist.district_id
            )
            db.add(new_hub)
            all_hubs_db.append(new_hub)
            
        db.flush()
        
        print("Đang tạo dữ liệu Vehicles (Phương tiện)...")
        # Danh sách mã vùng biển số xe các tỉnh miền Bắc để random cho giống thật
        plate_prefixes = [29, 30, 15, 16, 90, 89, 34, 14, 98, 19, 21, 22, 23, 88, 99, 17, 18, 35]
        
        for hub in all_hubs_db:
            # Mỗi hub có từ 1-3 xe
            num_vehicles = random.randint(1, 3)
            for _ in range(num_vehicles):
                v_model = random.choice(vehicle_models)
                # Tạo biển số ngẫu nhiên VD: 29C-123.45
                plate_prefix = random.choice(plate_prefixes)
                plate_letter = random.choice(['C', 'D', 'H'])
                plate_suffix = f"{random.randint(100, 999)}.{random.randint(10, 99)}"
                plate_number = f"{plate_prefix}{plate_letter}-{plate_suffix}"
                
                # Kiểm tra trùng lặp biển số (phòng trường hợp hiếm gặp)
                while db.query(Vehicles).filter(Vehicles.plate_number == plate_number).first():
                    plate_suffix = f"{random.randint(100, 999)}.{random.randint(10, 99)}"
                    plate_number = f"{plate_prefix}{plate_letter}-{plate_suffix}"

                new_vehicle = Vehicles(
                    vehicle_name=v_model,
                    plate_number=plate_number,
                    hub_id=hub.hub_id
                )
                db.add(new_vehicle)
                
        db.commit()
        print("Quá trình seed dữ liệu hoàn tất thành công!")
        
    except Exception as e:
        db.rollback()
        print(f"Lỗi trong quá trình seed dữ liệu: {e}")

if __name__ == "__main__":
    print("Bắt đầu chạy seed dữ liệu...")
    # Khởi tạo db session
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()

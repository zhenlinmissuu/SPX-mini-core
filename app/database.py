# app/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Chuỗi kết nối sử dụng tài khoản và DB mới tinh trong file .env
DATABASE_URL = "postgresql+asyncpg://spx_admin:1234@localhost:5432/spx_mini_db"

# Khởi tạo Async Engine cho dự án hiện tại
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,         # Tối ưu số lượng kết nối đồng thời cho script sinh 50k đơn hàng
    max_overflow=10
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


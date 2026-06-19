FROM python:3.10-slim

WORKDIR /code

# Cài đặt các dependencies hệ thống cần thiết cho psycopg2 (PostgreSQL driver)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Chạy FastAPI thông qua Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

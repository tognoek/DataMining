# Sử dụng image Python chính thức từ Docker Hub
FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các phụ thuộc từ requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Mở cổng mà ứng dụng sẽ chạy trên đó
EXPOSE 5000

# Lệnh để chạy ứng dụng
CMD ["python", "app.py"]

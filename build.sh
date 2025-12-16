#!/bin/bash
# Build script cho Render
# Render sẽ chạy script này trước khi start server

echo "Khởi tạo database..."
python -c "from models.database import init_db; init_db(); print('Database đã sẵn sàng!')"

echo "Build hoàn thành!"

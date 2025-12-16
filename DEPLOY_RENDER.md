# Hướng dẫn Deploy lên Render

## Chuẩn bị

### 1. Push code lên GitHub

```bash
# Tạo repo trên GitHub (nếu chưa có)
git init
git add .
git commit -m "Initial commit - movie recommender"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/KDDL_btl.git
git push -u origin main
```

### 2. Tạo tài khoản Render (miễn phí)
https://render.com

---

## Deploy từng bước

### Bước 1: Tạo PostgreSQL Database
1. Vào https://dashboard.render.com
2. Click **New +** → **PostgreSQL**
3. Điền:
   - **Name**: `movie-recommender-db`
   - **Database**: `movierecommender`
   - **User**: `postgres` (mặc định)
   - **Region**: Singapore hoặc gần bạn nhất
4. Click **Create Database**
5. **Sao chép connection string** (để dùng sau)

### Bước 2: Tạo Web Service
1. Click **New +** → **Web Service**
2. **Connect a repository**:
   - Click "Connect your GitHub account"
   - Select repo: `KDDL_btl`
   - Click **Connect**

3. **Cấu hình service**:
   - **Name**: `movie-recommender`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && bash build.sh`
   - **Start Command**: `gunicorn server:app`
   - **Region**: Giống database (Singapore)

4. **Thêm Environment Variables**:
   - Click **Environment**
   - Click **Add Environment Variable**
   - Thêm:
     ```
     DATABASE_URL = postgresql+psycopg2://postgres:PASSWORD@HOST/movierecommender
     ```
     (Lấy từ connection string của PostgreSQL ở Bước 1)
     Ví dụ:
     ```
     DATABASE_URL = postgresql+psycopg2://postgres:abc123@dpg-xyz.render.internal/movierecommender
     ```

5. Click **Create Web Service**

6. **Chờ deploy** (~2-3 phút)
   - Render sẽ:
     1. Clone code từ GitHub
     2. Cài dependencies từ `requirements.txt`
     3. Chạy `build.sh` (tạo bảng database)
     4. Start server với Gunicorn
     5. Deploy live

### Bước 3: Truy cập ứng dụng
- Sau khi deploy xong, Render cấp URL: `https://movie-recommender.onrender.com`
- Vào link đó để sử dụng!

---

## Deployment liên tục (Auto-deploy)

Bất cứ khi nào bạn push code lên GitHub:
```bash
git add .
git commit -m "Fix: xyz"
git push origin main
```

Render sẽ **tự động deploy** lên ~1-2 phút

---

## Troubleshooting

### 1. Lỗi database connection
```
ModuleNotFoundError: No module named 'psycopg2'
```
→ Đã fix rồi (thêm vào requirements.txt ✅)

### 2. Logs không hiển thị
→ Click **Logs** trong dashboard Render

### 3. Build script lỗi
```bash
# Test local trước:
pip install -r requirements.txt
bash build.sh
python server.py
```

### 4. Free tier sleep
- Render free web service sẽ ngủ sau 15 phút inactive
- Khi truy cập lại sẽ wake up (~30s)
- Để upgrade: Click **Settings** → **Plan** (từ $7/tháng)

---

## Tóm tắt

| Công việc | Hoàn thành |
|----------|-----------|
| requirements.txt | ✅ |
| build.sh | ✅ |
| database.py hỗ trợ PostgreSQL | ✅ |
| .gitignore | ✅ |
| Push GitHub | ⏳ Bạn làm |
| Tạo PostgreSQL trên Render | ⏳ Bạn làm |
| Tạo Web Service trên Render | ⏳ Bạn làm |
| Deploy live | ⏳ Sẽ tự động |

---

## Chi phí

- **PostgreSQL Database**: MIỄN PHÍ (750 giờ/tháng)
- **Web Service**: MIỄN PHÍ (ngủ sau 15p inactive)
- **Tổng cộng**: **$0** 💰

Nếu muốn app không ngủ: $7/tháng (Render Pro)

---

Bạn tạo tài khoản GitHub + Render rồi cho mình biết, mình sẽ hướng dẫn chi tiết từng bước nhé! 🚀

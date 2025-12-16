# Hướng dẫn cấu hình SQL Server

## 1. Dùng SQLite (mặc định - không cần config)

Hệ thống sẽ tự động dùng SQLite nếu không có config SQL Server.
File database: `data/user_history.db`

## 2. Kết nối SQL Server

### Bước 1: Cài đặt driver ODBC

Tải và cài **ODBC Driver 17 for SQL Server**:
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Bước 2: Cài đặt Python packages

```bash
pip install pyodbc sqlalchemy
```

### Bước 3: Tạo database trong SQL Server

```sql
CREATE DATABASE MovieRecommender;
```

### Bước 4: Thiết lập biến môi trường

**Windows PowerShell:**

```powershell
$env:DATABASE_URL="mssql+pyodbc://username:password@server/MovieRecommender?driver=ODBC+Driver+17+for+SQL+Server"
```

**Hoặc tạo file `.env`:**

```
DATABASE_URL=mssql+pyodbc://username:password@server/MovieRecommender?driver=ODBC+Driver+17+for+SQL+Server
```

### Ví dụ connection string

**SQL Server trên localhost:**

```
mssql+pyodbc://sa:MyPassword123@localhost/MovieRecommender?driver=ODBC+Driver+17+for+SQL+Server
```

**SQL Server Windows Authentication:**

```
mssql+pyodbc://localhost/MovieRecommender?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**SQL Server Azure:**

```
mssql+pyodbc://username:password@yourserver.database.windows.net/MovieRecommender?driver=ODBC+Driver+17+for+SQL+Server
```

## 3. Chạy server

```bash
python server.py
```

Server sẽ tự động tạo bảng `search_history` và `view_history` nếu chưa có.

## Cấu trúc bảng

### search_history

- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- user_id (VARCHAR(50), INDEX)
- query (VARCHAR(500))
- top_k (INT)
- result_count (INT)
- timestamp (DATETIME)

### view_history

- id (INT, PRIMARY KEY, AUTO_INCREMENT)
- user_id (VARCHAR(50), INDEX)
- movie_id (VARCHAR(50))
- title (VARCHAR(500))
- genres (VARCHAR(200))
- rating (FLOAT)
- timestamp (DATETIME)

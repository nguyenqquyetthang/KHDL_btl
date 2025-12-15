# Hệ thống gợi ý phim (Movie Recommendation System)

Dự án Flask minh họa pipeline recommendation content-based với TF-IDF + cosine similarity. Sử dụng dataset **Top 10000 Popular Movies** từ Kaggle (~10,000 phim với ratings, genres, overview).

## Cấu trúc

```
server.py
controllers/recommend_controller.py
models/
  ├── data_loader.py
  ├── data_cleaner.py
  ├── vectorizer.py
  ├── recommender.py
  └── metrics.py
views/
  ├── templates/index.html
  └── static/
      ├── style.css
      └── script.js
data/
  ├── raw/movies.csv
  └── processed/cleaned_movies.csv
scripts/
  ├── download_kaggle_movies.py
  └── download_dataset.py (Google Drive alternative)
```

## Dataset

**Top 10000 Popular Movies** từ Kaggle (~10,000 phim)

- Nguồn: https://www.kaggle.com/datasets/omkarborikar/top-10000-popular-movies
- Schema: title, overview, genres, release_date, vote_average, popularity, vote_count, etc.
- Đáp ứng yêu cầu: ≥2,000 items, ≥5 features

## Thiết lập

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình Kaggle API

- Đăng nhập Kaggle → Account → Create New API Token → tải `kaggle.json`
- Windows: đặt vào `C:\Users\<username>\.kaggle\kaggle.json`
- Linux/Mac: `~/.kaggle/kaggle.json` + `chmod 600 ~/.kaggle/kaggle.json`

### 3. Tải dataset

```bash
python scripts\download_kaggle_movies.py
```

Hoặc tải thủ công từ [Kaggle](https://www.kaggle.com/datasets/omkarborikar/top-10000-popular-movies) và đặt CSV vào `data/raw/movies.csv`.

### 4. Chạy server

```bash
python server.py
```

Truy cập: http://localhost:5000

## Thành phần chính

### Models (Pipeline)

- `data_loader.py`: Đọc raw data, cache processed data
- `data_cleaner.py`:
  - Xử lý missing values (overview, genres)
  - Parse genres từ JSON format
  - Chuẩn hóa text (normalize Unicode, lowercase)
  - Loại bỏ duplicate (title + release_date)
  - Clamp outlier rating (0-10)
  - Build `combined_text` từ title + overview + genres
- `vectorizer.py`: TF-IDF bigram (max_features=6000, min_df=2, stop_words='english')
- `recommender.py`: Cosine similarity, trả về top-k phim
- `metrics.py`:
  - Rating distribution (0-10 scale)
  - Genre frequency (top 15)
  - Top items theo vote_average

### Controllers (API)

- `POST /api/recommend`: body `{"query": "action space", "top_k": 10}` → danh sách phim gợi ý
- `GET /api/stats`: thống kê cho biểu đồ (rating, genres, top movies)
- `GET /api/health`: kiểm tra status

### Views (Frontend)

- Form tìm kiếm phim (từ khóa, thể loại)
- Hiển thị kết quả: title, genres, rating, release year, overview preview, similarity score
- 3 biểu đồ Chart.js: phân bố rating, tần suất thể loại, top 15 phim

## Quy trình dữ liệu

```
data/raw/movies.csv (Kaggle dataset)
         ↓
   load_raw_data()
         ↓
   clean_data() [xử lý missing, parse genres, normalize, build combined_text]
         ↓
   save_processed_data()
         ↓
data/processed/cleaned_movies.csv (cached)
         ↓
   build_vectorizer() [TF-IDF]
         ↓
   ContentRecommender [cosine similarity]
         ↓
   API /api/recommend, /api/stats
```

## Đáp ứng yêu cầu

### 1. Thu thập dữ liệu

✅ Dataset ~10,000 phim từ Kaggle (≥2,000 items)  
✅ ≥5 features: title, overview, genres, release_date, vote_average, popularity, vote_count

### 2. Làm sạch dữ liệu (≥3 tác vụ)

✅ Missing values: fill overview, genres với "unknown"  
✅ Chuẩn hóa: normalize Unicode, lowercase, remove extra spaces  
✅ Loại bỏ duplicate: theo title + release_date  
✅ Xử lý outlier: clamp vote_average (0-10)  
✅ Vector hóa: TF-IDF bigram

### 3. Trực quan hóa (≥3 tác vụ)

✅ Phân bố rating (histogram 10 bins, 0-10 scale)  
✅ Tần suất thể loại (bar chart top 15)  
✅ Top items (top 15 phim theo vote_average)

### 4. Xây dựng mô hình recommendation

✅ Content-based: TF-IDF + cosine similarity  
✅ Input: query text → Output: top-k phim tương tự

### 5. Hiển thị gợi ý

✅ Form nhập query  
✅ Danh sách kết quả với thông tin đầy đủ  
✅ Biểu đồ thống kê

## API Examples

### Gợi ý phim

```bash
curl -X POST http://localhost:5000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "space adventure sci-fi", "top_k": 5}'
```

Response:

```json
{
  "results": [
    {
      "id": 123,
      "title": "Interstellar",
      "overview": "A team of explorers travel through a wormhole...",
      "genres": "Adventure, Drama, Science Fiction",
      "rating": 8.3,
      "release_date": "2014-11-07",
      "year": 2014,
      "score": 0.85
    }
  ]
}
```

### Thống kê

```bash
curl http://localhost:5000/api/stats
```

## Ghi chú

- Lần đầu chạy: hệ thống tự làm sạch và cache vào `data/processed/cleaned_movies.csv`
- Thay dataset: xóa file processed, hệ thống sẽ tự rebuild
- Frontend dùng Chart.js cho biểu đồ, không cần matplotlib/seaborn
- Mô hình là content-based đơn giản, có thể mở rộng: collaborative filtering, hybrid, deep learning embeddings

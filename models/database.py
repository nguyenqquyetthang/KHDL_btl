from __future__ import annotations

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class SearchHistory(Base):
    """Bảng lưu lịch sử tìm kiếm."""
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    query = Column(String(500), nullable=False)
    top_k = Column(Integer, nullable=False)
    result_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)


class ViewHistory(Base):
    """Bảng lưu lịch sử xem phim."""
    __tablename__ = "view_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False, index=True)
    movie_id = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    genres = Column(String(200), nullable=True)
    rating = Column(Float, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.now)


def get_database_url():
    """Lấy connection string từ biến môi trường hoặc dùng SQLite mặc định."""
    # Render cung cấp DATABASE_URL với format: postgresql://user:password@host/dbname
    # Local dùng: mssql+pyodbc://... hoặc sqlite://...
    
    db_url = os.getenv("DATABASE_URL")
    
    if not db_url:
        # Fallback sang SQLite nếu không có config
        db_url = "sqlite:///data/user_history.db"
    
    # Render sử dụng postgresql:// thay vì postgresql+psycopg2://
    # SQLAlchemy yêu cầu postgresql+psycopg2:// nên chuyển đổi
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    return db_url


def get_engine():
    """Tạo SQLAlchemy engine."""
    db_url = get_database_url()
    
    # Nếu dùng SQLite, thêm check_same_thread=False
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_pre_ping=True)
    
    return engine


def init_db():
    """Khởi tạo database: tạo bảng nếu chưa có."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session():
    """Lấy session để thao tác với database."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

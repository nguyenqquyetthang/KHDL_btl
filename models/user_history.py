from __future__ import annotations

from datetime import datetime
from typing import Any
from sqlalchemy import desc

from models.database import get_session, SearchHistory, ViewHistory


class UserHistory:
    """Quản lý lịch sử tìm kiếm và xem phim của người dùng (dùng SQL)."""

    def __init__(self, user_id: str = "default"):
        self.user_id = user_id

    def add_search(self, query: str, top_k: int, result_count: int) -> None:
        """Thêm một lần tìm kiếm vào lịch sử."""
        session = get_session()
        try:
            search = SearchHistory(
                user_id=self.user_id,
                query=query,
                top_k=top_k,
                result_count=result_count,
                timestamp=datetime.now()
            )
            session.add(search)
            session.commit()
            
            # Giữ 50 tìm kiếm gần nhất, xóa cũ hơn
            old_searches = (
                session.query(SearchHistory)
                .filter(SearchHistory.user_id == self.user_id)
                .order_by(desc(SearchHistory.timestamp))
                .offset(50)
                .all()
            )
            for old in old_searches:
                session.delete(old)
            session.commit()
        finally:
            session.close()

    def add_view(self, movie_id: int | str, title: str, genres: str, rating: float) -> None:
        """Thêm một phim đã xem vào lịch sử."""
        session = get_session()
        try:
            # Xóa bản ghi cũ của phim này nếu có (để cập nhật timestamp)
            session.query(ViewHistory).filter(
                ViewHistory.user_id == self.user_id,
                ViewHistory.movie_id == str(movie_id)
            ).delete()
            
            view = ViewHistory(
                user_id=self.user_id,
                movie_id=str(movie_id),
                title=title,
                genres=genres,
                rating=rating,
                timestamp=datetime.now()
            )
            session.add(view)
            session.commit()
            
            # Giữ 30 phim gần nhất
            old_views = (
                session.query(ViewHistory)
                .filter(ViewHistory.user_id == self.user_id)
                .order_by(desc(ViewHistory.timestamp))
                .offset(30)
                .all()
            )
            for old in old_views:
                session.delete(old)
            session.commit()
        finally:
            session.close()

    def get_searches(self, limit: int = 10) -> list[dict[str, Any]]:
        """Lấy lịch sử tìm kiếm gần nhất."""
        session = get_session()
        try:
            searches = (
                session.query(SearchHistory)
                .filter(SearchHistory.user_id == self.user_id)
                .order_by(desc(SearchHistory.timestamp))
                .limit(limit)
                .all()
            )
            return [
                {
                    "query": s.query,
                    "top_k": s.top_k,
                    "result_count": s.result_count,
                    "timestamp": s.timestamp.isoformat()
                }
                for s in searches
            ]
        finally:
            session.close()

    def get_views(self, limit: int = 10) -> list[dict[str, Any]]:
        """Lấy lịch sử xem phim gần nhất."""
        session = get_session()
        try:
            views = (
                session.query(ViewHistory)
                .filter(ViewHistory.user_id == self.user_id)
                .order_by(desc(ViewHistory.timestamp))
                .limit(limit)
                .all()
            )
            return [
                {
                    "movie_id": v.movie_id,
                    "title": v.title,
                    "genres": v.genres,
                    "rating": v.rating,
                    "timestamp": v.timestamp.isoformat()
                }
                for v in views
            ]
        finally:
            session.close()

    def get_all_history(self) -> dict[str, list]:
        """Lấy toàn bộ lịch sử."""
        return {
            "searches": self.get_searches(limit=1000),
            "views": self.get_views(limit=1000)
        }

    def clear_history(self) -> None:
        """Xóa toàn bộ lịch sử."""
        session = get_session()
        try:
            session.query(SearchHistory).filter(
                SearchHistory.user_id == self.user_id
            ).delete()
            session.query(ViewHistory).filter(
                ViewHistory.user_id == self.user_id
            ).delete()
            session.commit()
        finally:
            session.close()


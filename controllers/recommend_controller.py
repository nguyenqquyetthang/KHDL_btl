from __future__ import annotations

from flask import Blueprint, jsonify, request

from models.data_loader import ensure_processed_data
from models.vectorizer import build_vectorizer, transform_query
from models.recommender import ContentRecommender
from models import metrics

recommend_bp = Blueprint("recommend", __name__)


_recommender: ContentRecommender | None = None


def _load_artifacts() -> ContentRecommender:
    global _recommender
    if _recommender is not None:
        return _recommender

    df = ensure_processed_data()
    vectorizer, matrix = build_vectorizer(df["combined_text"].tolist())
    _recommender = ContentRecommender(df=df, vectorizer=vectorizer, matrix=matrix)
    return _recommender


@recommend_bp.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@recommend_bp.route("/api/recommend", methods=["POST"])
def recommend():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query", "").strip()
    top_k = payload.get("top_k", 10)

    if not query:
        return jsonify({"error": "Vui lòng nhập từ khóa hoặc mô tả"}), 400

    try:
        top_k = int(top_k)
    except (TypeError, ValueError):
        top_k = 10

    recommender = _load_artifacts()
    query_vec = transform_query(recommender.vectorizer, query)
    results = recommender.recommend_by_query(query_vec=query_vec, top_k=top_k)
    return jsonify({"results": results})


@recommend_bp.route("/api/stats", methods=["GET"])
def stats():
    recommender = _load_artifacts()
    df = recommender.df

    rating_dist = metrics.rating_distribution(df)
    genre_counts = metrics.genre_frequency(df, top_n=15)
    top_items = metrics.top_items(df, top_n=15)

    return jsonify(
        {
            "rating_distribution": rating_dist,
            "genre_counts": genre_counts,
            "top_items": top_items,
        }
    )

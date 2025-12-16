from __future__ import annotations

import numpy as np
import pandas as pd


def rating_distribution(df: pd.DataFrame, bins: int = 20):
    rating_col = "vote_average" if "vote_average" in df.columns else "rating"
    ratings = df[rating_col].astype(float)
    max_rating = 10 if "vote_average" in df.columns else 5
    hist, bin_edges = np.histogram(ratings, bins=bins, range=(0, max_rating))
    return {
        "bins": bin_edges.tolist(),
        "counts": hist.tolist(),
    }


def genre_frequency(df: pd.DataFrame, top_n: int = 10):
    genre_col = "genres" if "genres" in df.columns else "genre"
    counts = (
        df[genre_col].astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .value_counts()
        .head(top_n)
    )
    return {
        "labels": counts.index.tolist(),
        "counts": counts.values.tolist(),
    }


def top_items(df: pd.DataFrame, top_n: int = 10):
    rating_col = "vote_average" if "vote_average" in df.columns else "rating"
    title_col = "original_title" if "original_title" in df.columns else "title"
    top = df.sort_values(by=rating_col, ascending=False).head(top_n)
    return {
        "titles": top[title_col].tolist(),
        "ratings": top[rating_col].astype(float).tolist(),
    }


def similarity_heatmap(df: pd.DataFrame, matrix, top_n: int = 10):
    """Build heatmap data (labels + similarity matrix) for top movies.

    - Chọn top_n theo vote_count (ưu tiên phim phổ biến để dễ đọc)
    - Tính cosine similarity từ TF-IDF matrix đã có
    - Trả về ma trận (list of list) và nhãn
    """

    if matrix is None or len(df) == 0:
        return {"labels": [], "matrix": []}

    df = df.copy()
    if "vote_count" in df.columns:
        df["__score"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
    elif "popularity" in df.columns:
        df["__score"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)
    else:
        rating_col = "vote_average" if "vote_average" in df.columns else "rating"
        df["__score"] = pd.to_numeric(df[rating_col], errors="coerce").fillna(0)

    top = df.sort_values(by="__score", ascending=False).head(top_n)
    idx = top.index.to_list()

    title_col = "original_title" if "original_title" in top.columns else "title"
    labels = top[title_col].fillna("(unknown)").tolist()

    sub_matrix = matrix[idx]
    sim = sub_matrix @ sub_matrix.T
    sim_dense = sim.toarray() if hasattr(sim, "toarray") else sim
    sim_dense = np.clip(sim_dense, 0, 1)
    return {"labels": labels, "matrix": sim_dense.round(3).tolist()}


def precision_at_k(relevant_items: set, recommended_items: list, k: int) -> float:
    if k == 0:
        return 0.0
    hits = sum(1 for item in recommended_items[:k] if item in relevant_items)
    return hits / k


def recall_at_k(relevant_items: set, recommended_items: list, k: int) -> float:
    if not relevant_items:
        return 0.0
    found = sum(1 for item in recommended_items[:k] if item in relevant_items)
    return found / len(relevant_items)


def mae(actual: list[float], predicted: list[float]) -> float:
    if not actual or not predicted or len(actual) != len(predicted):
        return 0.0
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.mean(np.abs(a - p)))


def rmse(actual: list[float], predicted: list[float]) -> float:
    if not actual or not predicted or len(actual) != len(predicted):
        return 0.0
    a = np.asarray(actual, dtype=float)
    p = np.asarray(predicted, dtype=float)
    return float(np.sqrt(np.mean((a - p) ** 2)))

from __future__ import annotations

import numpy as np
import pandas as pd


def rating_distribution(df: pd.DataFrame, bins: int = 10):
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


def precision_at_k(relevant_items: set, recommended_items: list, k: int) -> float:
    if k == 0:
        return 0.0
    hits = sum(1 for item in recommended_items[:k] if item in relevant_items)
    return hits / k

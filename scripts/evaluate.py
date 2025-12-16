from __future__ import annotations

import argparse
import numpy as np
import pandas as pd

from models.data_loader import ensure_processed_data
from models.vectorizer import build_vectorizer
from models.recommender import ContentRecommender
from models import metrics


def baseline_rating_predictions(df: pd.DataFrame) -> tuple[list[float], list[float]]:
    """Return actual and baseline-predicted ratings.

    Baseline: predict every item's rating as the global mean.
    """
    rating_col = "vote_average" if "vote_average" in df.columns else "rating"
    ratings = pd.to_numeric(df[rating_col], errors="coerce").fillna(0).astype(float)
    mean_rating = float(ratings.mean())
    predicted = [mean_rating] * len(ratings)
    return ratings.tolist(), predicted


def build_recommender(df: pd.DataFrame) -> ContentRecommender:
    texts = df["combined_text"].astype(str).tolist()
    vectorizer, matrix = build_vectorizer(texts)
    return ContentRecommender(df=df, vectorizer=vectorizer, matrix=matrix)


def compute_precision_recall(df: pd.DataFrame, recommender: ContentRecommender, k: int, sample: int | None = None) -> tuple[float, float]:
    """Evaluate Precision@K and Recall@K by genre-based relevance.

    Relevance definition: items that share at least one genre with the query movie.
    For each movie i, use its own `combined_text` as a query to retrieve top-K similar movies.
    Exclude the movie itself from recommendations when computing metrics.
    """
    genre_col = "genres" if "genres" in df.columns else "genre"
    titles_col = "original_title" if "original_title" in df.columns else "title"

    # Precompute genre sets per item
    genre_sets = df[genre_col].astype(str).str.split(",").apply(lambda xs: {x.strip() for x in xs if x.strip()})

    # Build query vectors for each item
    queries = df["combined_text"].astype(str).tolist()
    query_vecs = recommender.vectorizer.transform(queries)

    indices = list(range(len(df)))
    if sample is not None and sample < len(indices):
        rng = np.random.default_rng(0)
        indices = rng.choice(indices, size=sample, replace=False).tolist()

    precision_list: list[float] = []
    recall_list: list[float] = []

    for i in indices:
        # Relevant set: items sharing at least one genre with i (excluding i)
        gi = genre_sets.iloc[i]
        relevant_idx = [j for j in range(len(df)) if j != i and len(gi & genre_sets.iloc[j]) > 0]
        relevant_titles = {df.iloc[j][titles_col] for j in relevant_idx}

        # Recommend by query for item i
        qv = query_vecs[i]
        results = recommender.recommend_by_query(qv, top_k=k + 1)  # +1 to allow self
        # Filter out self item by title match
        rec_titles = [r["title"] for r in results if r["title"] != df.iloc[i][titles_col]][:k]

        p = metrics.precision_at_k(relevant_titles, rec_titles, k)
        r = metrics.recall_at_k(relevant_titles, rec_titles, k)
        precision_list.append(p)
        recall_list.append(r)

    precision = float(np.mean(precision_list)) if precision_list else 0.0
    recall = float(np.mean(recall_list)) if recall_list else 0.0
    return precision, recall



def main():
    parser = argparse.ArgumentParser(description="Evaluate recommender metrics")
    parser.add_argument("--k", type=int, default=10, help="Top-K for Precision/Recall")
    parser.add_argument("--sample", type=int, default=200, help="Number of items to sample for P/R evaluation (None for all)")
    args = parser.parse_args()

    df = ensure_processed_data()
    recommender = build_recommender(df)

    # Rating prediction errors (baseline)
    actual, predicted = baseline_rating_predictions(df)
    mae_val = metrics.mae(actual, predicted)
    rmse_val = metrics.rmse(actual, predicted)

    # Precision/Recall@K (genre-based relevance)
    precision_k, recall_k = compute_precision_recall(df, recommender, k=args.k, sample=args.sample)

    print(f"MAE (baseline): {mae_val:.4f}")
    print(f"RMSE (baseline): {rmse_val:.4f}")
    print(f"Precision@{args.k}: {precision_k:.4f}")
    print(f"Recall@{args.k}: {recall_k:.4f}")


if __name__ == "__main__":
    main()

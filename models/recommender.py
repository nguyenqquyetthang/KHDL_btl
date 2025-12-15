from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer


class ContentRecommender:
    def __init__(self, df: pd.DataFrame, vectorizer: TfidfVectorizer, matrix):
        self.df = df
        self.vectorizer = vectorizer
        self.matrix = matrix

    def recommend_by_query(self, query_vec, top_k: int = 10):
        similarities = linear_kernel(query_vec, self.matrix).flatten()
        top_k = max(1, min(top_k, len(similarities)))
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            row = self.df.iloc[idx]
            rating_col = "vote_average" if "vote_average" in row else "rating"
            title = row.get("original_title", row.get("title", ""))
            genres = row.get("genre", row.get("genres", ""))
            results.append(
                {
                    "id": int(row.get("id", idx)),
                    "title": title,
                    "overview": row.get("overview", row.get("description", "")),
                    "genres": genres,
                    "rating": float(row.get(rating_col, 0)),
                    "release_date": str(row.get("release_date", "")),
                    "year": int(row.get("year", 0)) if not pd.isna(row.get("year", np.nan)) else None,
                    "score": float(similarities[idx]),
                }
            )
        return results

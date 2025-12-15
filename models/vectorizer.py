from __future__ import annotations

from typing import Iterable, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer


def build_vectorizer(corpus: Iterable[str], max_features: int = 6000) -> Tuple[TfidfVectorizer, object]:
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),
        min_df=2,
        stop_words="english",
    )
    matrix = vectorizer.fit_transform(corpus)
    return vectorizer, matrix


def transform_query(vectorizer: TfidfVectorizer, query: str):
    return vectorizer.transform([query])

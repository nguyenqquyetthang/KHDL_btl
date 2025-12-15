from __future__ import annotations

import re
import json
import unicodedata
import numpy as np
import pandas as pd


TEXT_COLS = ["original_title", "overview", "genre", "original_language"]


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"\s+", " ", ascii_text)
    return ascii_text.strip().lower()


def _parse_genres(genres_str):
    """Parse genres from string list format like ['Action', 'Adventure']"""
    if pd.isna(genres_str) or genres_str == "":
        return "unknown"
    if isinstance(genres_str, str):
        # Handle format: ['Action', 'Adventure', 'Science Fiction']
        try:
            # Remove brackets and quotes, split by comma
            genres_str = genres_str.strip("[]")
            genres_list = [g.strip().strip("'\"") for g in genres_str.split(',')]
            return ', '.join(genres_list) if genres_list and genres_list[0] else "unknown"
        except Exception:
            return str(genres_str)
    return "unknown"


def _fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    filled = df.copy()
    for col in TEXT_COLS:
        if col in filled.columns:
            if col == "genre":
                filled[col] = filled[col].apply(_parse_genres)
            else:
                filled[col] = filled[col].fillna("unknown")
    if "vote_average" in filled.columns:
        filled["vote_average"] = filled["vote_average"].fillna(filled["vote_average"].median())
    elif "rating" in filled.columns:
        filled["rating"] = filled["rating"].fillna(filled["rating"].median())
    return filled


def _drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    if "original_title" in df.columns and "release_date" in df.columns:
        return df.drop_duplicates(subset=["original_title", "release_date"], keep="first")
    elif "original_title" in df.columns:
        return df.drop_duplicates(subset=["original_title"], keep="first")
    elif "title" in df.columns and "release_date" in df.columns:
        return df.drop_duplicates(subset=["title", "release_date"], keep="first")
    elif "title" in df.columns:
        return df.drop_duplicates(subset=["title"], keep="first")
    return df.drop_duplicates()


def _clamp_rating(df: pd.DataFrame) -> pd.DataFrame:
    rating_col = "vote_average" if "vote_average" in df.columns else "rating"
    if rating_col not in df.columns:
        return df
    df = df.copy()
    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df[rating_col] = df[rating_col].clip(lower=0, upper=10)
    df[rating_col] = df[rating_col].fillna(df[rating_col].median())
    return df


def _build_combined_text(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    available_cols = [c for c in TEXT_COLS if c in df.columns]
    if not available_cols:
        raise ValueError(f"Khong co cot text nao trong TEXT_COLS")

    text_parts = [df[col].astype(str) for col in available_cols]
    df["combined_text"] = (
        " ".join([df[col].astype(str) for col in available_cols])
        if len(available_cols) == 1
        else text_parts[0]
    )
    for part in text_parts[1:]:
        df["combined_text"] = df["combined_text"] + " " + part
    
    df["combined_text"] = df["combined_text"].apply(_normalize_text)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = _fill_missing(df)
    cleaned = _drop_duplicates(cleaned)
    cleaned = _clamp_rating(cleaned)
    cleaned = _build_combined_text(cleaned)

    if "release_date" in cleaned.columns:
        cleaned["release_date"] = pd.to_datetime(cleaned["release_date"], errors="coerce")
        cleaned["year"] = cleaned["release_date"].dt.year
        cleaned["year"] = cleaned["year"].fillna(cleaned["year"].median())
    elif "year" in cleaned.columns:
        cleaned["year"] = pd.to_numeric(cleaned["year"], errors="coerce")
        cleaned["year"] = cleaned["year"].fillna(cleaned["year"].median())

    cleaned.reset_index(drop=True, inplace=True)
    return cleaned

from __future__ import annotations

from pathlib import Path
import pandas as pd

from models.data_cleaner import clean_data

RAW_PATH = Path("data/raw/movies.csv")
PROCESSED_PATH = Path("data/processed/cleaned_movies.csv")


def load_raw_data() -> pd.DataFrame:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file dữ liệu gốc: {RAW_PATH}")
    return pd.read_csv(
        RAW_PATH,
        encoding='utf-8',
        on_bad_lines='skip',
        engine='python',
        quoting=1  # QUOTE_ALL
    )


def load_processed_data() -> pd.DataFrame | None:
    if PROCESSED_PATH.exists():
        return pd.read_csv(PROCESSED_PATH)
    return None


def save_processed_data(df: pd.DataFrame) -> None:
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)


def ensure_processed_data() -> pd.DataFrame:
    processed = load_processed_data()
    if processed is not None:
        return processed

    raw = load_raw_data()
    processed = clean_data(raw)
    save_processed_data(processed)
    return processed

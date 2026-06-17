"""Shared preprocessing helpers for Alpha Factory datasets."""

from dataclasses import dataclass
from typing import List, Optional

import pandas as pd


@dataclass(frozen=True)
class PreparedDataset:
    raw: pd.DataFrame
    train_raw: pd.DataFrame
    test_raw: pd.DataFrame
    train: pd.DataFrame
    test: pd.DataFrame
    feature_cols: List[str]
    price_col: str
    mu: pd.Series
    sigma: pd.Series
    split_idx: int


def load_numeric_frame(path: str, *, drop_unnamed: bool = True) -> pd.DataFrame:
    frame = pd.read_csv(path)

    if drop_unnamed and "Unnamed: 0" in frame.columns:
        frame = frame.drop(columns=["Unnamed: 0"])

    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame


def prepare_train_test_frame(
    raw: pd.DataFrame,
    *,
    price_col: str = "price",
    train_fraction: float = 0.7,
    clip_value: float = 5.0,
) -> PreparedDataset:
    if price_col not in raw.columns:
        raise ValueError(f"Expected '{price_col}' column in input data")

    split_idx = int(len(raw) * train_fraction)
    train_raw = raw.iloc[:split_idx].copy()
    test_raw = raw.iloc[split_idx:].copy()

    feature_cols = [column for column in raw.columns if column != price_col]
    mu = train_raw[feature_cols].mean()
    sigma = train_raw[feature_cols].std().replace(0, 1.0)

    train = train_raw.copy()
    test = test_raw.copy()

    train[feature_cols] = (train_raw[feature_cols] - mu) / sigma
    test[feature_cols] = (test_raw[feature_cols] - mu) / sigma

    if clip_value is not None:
        train[feature_cols] = train[feature_cols].clip(-clip_value, clip_value)
        test[feature_cols] = test[feature_cols].clip(-clip_value, clip_value)

    train = train.fillna(0.0)
    test = test.fillna(0.0)

    return PreparedDataset(
        raw=raw.copy(),
        train_raw=train_raw,
        test_raw=test_raw,
        train=train,
        test=test,
        feature_cols=feature_cols,
        price_col=price_col,
        mu=mu,
        sigma=sigma,
        split_idx=split_idx,
    )


def prepare_dataset_from_csv(
    path: str,
    *,
    price_col: str = "price",
    train_fraction: float = 0.7,
    clip_value: float = 5.0,
) -> PreparedDataset:
    raw = load_numeric_frame(path)
    return prepare_train_test_frame(
        raw,
        price_col=price_col,
        train_fraction=train_fraction,
        clip_value=clip_value,
    )


def normalize_external_frame(
    raw: pd.DataFrame,
    *,
    feature_cols: List[str],
    mu: pd.Series,
    sigma: pd.Series,
    price_col: str = "price",
    clip_value: Optional[float] = 5.0,
) -> pd.DataFrame:
    if price_col not in raw.columns:
        raise ValueError(f"Expected '{price_col}' column in external data")

    missing = [column for column in feature_cols if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing feature columns in external data: {missing[:8]}")

    frame = raw.copy()
    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame[feature_cols] = (frame[feature_cols] - mu) / sigma
    if clip_value is not None:
        frame[feature_cols] = frame[feature_cols].clip(-clip_value, clip_value)

    return frame.fillna(0.0)

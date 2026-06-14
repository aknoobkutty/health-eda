"""CSV loading, profiling, and type inference helpers."""

from __future__ import annotations

from dataclasses import dataclass
from io import StringIO

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ColumnGroups:
    numerical: list[str]
    categorical: list[str]
    datetime: list[str]
    boolean: list[str]


def read_csv(uploaded_file) -> pd.DataFrame:
    """Read a CSV upload with practical defaults and fallback encodings."""
    if uploaded_file is None:
        raise ValueError("No file uploaded.")

    uploaded_file.seek(0)
    try:
        return pd.read_csv(uploaded_file)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding="latin-1")
    except pd.errors.ParserError:
        uploaded_file.seek(0)
        text = uploaded_file.getvalue().decode("utf-8", errors="replace")
        return pd.read_csv(StringIO(text), sep=None, engine="python")


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from column names while preserving user-visible labels."""
    cleaned = df.copy()
    cleaned.columns = [str(col).strip() for col in cleaned.columns]
    return cleaned


def infer_column_groups(df: pd.DataFrame) -> ColumnGroups:
    """Infer numerical, categorical, datetime, and boolean columns."""
    numerical = df.select_dtypes(include=[np.number]).columns.tolist()
    boolean = df.select_dtypes(include=["bool"]).columns.tolist()

    datetime_cols: list[str] = []
    for col in df.columns:
        if col in numerical or col in boolean:
            continue
        sample = df[col].dropna().astype(str).head(200)
        if sample.empty:
            continue
        parsed = pd.to_datetime(sample, errors="coerce", utc=False)
        if parsed.notna().mean() >= 0.8:
            datetime_cols.append(col)

    categorical = [
        col
        for col in df.columns
        if col not in numerical and col not in datetime_cols and col not in boolean
    ]

    low_cardinality_numeric = [
        col
        for col in numerical
        if df[col].nunique(dropna=True) <= min(20, max(2, int(len(df) * 0.05)))
    ]
    categorical = categorical + low_cardinality_numeric

    return ColumnGroups(
        numerical=numerical,
        categorical=list(dict.fromkeys(categorical)),
        datetime=datetime_cols,
        boolean=boolean,
    )


def dataset_overview(df: pd.DataFrame) -> dict[str, object]:
    """Return high-level dataset information."""
    total_cells = int(df.shape[0] * df.shape[1])
    missing_cells = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    memory_mb = float(df.memory_usage(deep=True).sum() / (1024**2))
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_cells": missing_cells,
        "missing_pct": round((missing_cells / total_cells * 100), 2) if total_cells else 0,
        "duplicate_rows": duplicate_rows,
        "duplicate_pct": round((duplicate_rows / len(df) * 100), 2) if len(df) else 0,
        "memory_mb": round(memory_mb, 2),
    }


def dataframe_info(df: pd.DataFrame) -> pd.DataFrame:
    """Return a compact DataFrame information table."""
    info = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": [str(dtype) for dtype in df.dtypes],
            "Non-Null Count": [int(df[col].notna().sum()) for col in df.columns],
            "Null Count": [int(df[col].isna().sum()) for col in df.columns],
            "Null %": [round(df[col].isna().mean() * 100, 2) for col in df.columns],
            "Unique Values": [int(df[col].nunique(dropna=True)) for col in df.columns],
        }
    )
    return info


def safe_numeric_df(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Return selected columns coerced to numeric and with all-empty columns removed."""
    cols = columns if columns is not None else df.columns.tolist()
    numeric = df[cols].apply(pd.to_numeric, errors="coerce")
    return numeric.dropna(axis=1, how="all")

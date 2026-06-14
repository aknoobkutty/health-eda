"""Statistical, correlation, transformation, and outlier helpers."""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
from scipy import stats


def summary_statistics(df: pd.DataFrame, numerical: list[str], categorical: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return numerical and categorical summary statistics."""
    numeric_summary = df[numerical].describe().T if numerical else pd.DataFrame()
    if not numeric_summary.empty:
        numeric_summary["skewness"] = df[numerical].skew(numeric_only=True)
        numeric_summary["kurtosis"] = df[numerical].kurtosis(numeric_only=True)

    categorical_summary = pd.DataFrame()
    if categorical:
        rows = []
        for col in categorical:
            mode = df[col].mode(dropna=True)
            rows.append(
                {
                    "column": col,
                    "unique": int(df[col].nunique(dropna=True)),
                    "top": mode.iloc[0] if not mode.empty else None,
                    "top_frequency": int(df[col].value_counts(dropna=True).iloc[0]) if df[col].nunique(dropna=True) else 0,
                    "missing": int(df[col].isna().sum()),
                }
            )
        categorical_summary = pd.DataFrame(rows)
    return numeric_summary, categorical_summary


def correlation_matrix(df: pd.DataFrame, numerical: list[str], method: str = "pearson") -> pd.DataFrame:
    """Compute a numeric correlation matrix."""
    if len(numerical) < 2:
        return pd.DataFrame()
    return df[numerical].corr(method=method)


def strong_correlations(corr: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame:
    """Extract strong positive and negative correlation pairs."""
    if corr.empty:
        return pd.DataFrame(columns=["Feature 1", "Feature 2", "Correlation", "Direction"])

    rows = []
    for c1, c2 in itertools.combinations(corr.columns, 2):
        value = corr.loc[c1, c2]
        if pd.notna(value) and abs(value) >= threshold:
            rows.append(
                {
                    "Feature 1": c1,
                    "Feature 2": c2,
                    "Correlation": round(float(value), 4),
                    "Direction": "Positive" if value > 0 else "Negative",
                }
            )
    return pd.DataFrame(rows).sort_values("Correlation", key=lambda s: s.abs(), ascending=False) if rows else pd.DataFrame(rows)


def chi_square_test(df: pd.DataFrame, col_a: str, col_b: str) -> dict[str, float | int]:
    """Run a Chi-Square independence test between two categorical columns."""
    table = pd.crosstab(df[col_a], df[col_b])
    chi2, p_value, dof, _ = stats.chi2_contingency(table)
    return {"chi2": float(chi2), "p_value": float(p_value), "degrees_of_freedom": int(dof)}


def anova_test(df: pd.DataFrame, category_col: str, numeric_col: str) -> dict[str, float | int]:
    """Run one-way ANOVA for a numeric column across category groups."""
    working = df[[category_col, numeric_col]].dropna()
    groups = [
        group[numeric_col].astype(float).values
        for _, group in working.groupby(category_col)
        if len(group) >= 2
    ]
    if len(groups) < 2:
        raise ValueError("ANOVA requires at least two groups with two or more observations.")
    f_stat, p_value = stats.f_oneway(*groups)
    return {"f_statistic": float(f_stat), "p_value": float(p_value), "groups_tested": int(len(groups))}


def distribution_tests(df: pd.DataFrame, numerical: list[str]) -> pd.DataFrame:
    """Compute skewness, kurtosis, and normality tests for numeric columns."""
    rows = []
    for col in numerical:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) < 3:
            continue
        sample = series.sample(5000, random_state=42) if len(series) > 5000 else series
        if len(sample) <= 5000:
            stat, p_value = stats.shapiro(sample)
            test_name = "Shapiro-Wilk"
        else:
            stat, p_value = stats.normaltest(sample)
            test_name = "D'Agostino K-squared"
        rows.append(
            {
                "Column": col,
                "Skewness": round(float(series.skew()), 4),
                "Kurtosis": round(float(series.kurtosis()), 4),
                "Normality Test": test_name,
                "Statistic": round(float(stat), 4),
                "p-value": round(float(p_value), 6),
                "Likely Normal": "Yes" if p_value >= 0.05 else "No",
            }
        )
    return pd.DataFrame(rows)


def iqr_outliers(df: pd.DataFrame, column: str) -> dict[str, object]:
    """Detect outliers with the IQR method."""
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    q1 = float(series.quantile(0.25))
    q3 = float(series.quantile(0.75))
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    mask = (series < lower) | (series > upper)
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower": lower,
        "upper": upper,
        "count": int(mask.sum()),
        "percentage": round(float(mask.mean() * 100), 2) if len(series) else 0,
        "values": series[mask],
    }


def log_transform(series: pd.Series) -> pd.Series:
    """Apply a safe log1p transformation, shifting values if needed."""
    numeric = pd.to_numeric(series, errors="coerce")
    min_value = numeric.min(skipna=True)
    shift = 0 if pd.isna(min_value) or min_value >= 0 else abs(float(min_value)) + 1
    return np.log1p(numeric + shift)


def boxcox_transform(series: pd.Series) -> tuple[pd.Series, float]:
    """Apply Box-Cox transformation to positive numeric values."""
    numeric = pd.to_numeric(series, errors="coerce")
    min_value = numeric.min(skipna=True)
    shifted = numeric.copy()
    if pd.isna(min_value):
        raise ValueError("Column contains no numeric values.")
    if min_value <= 0:
        shifted = shifted + abs(float(min_value)) + 1
    transformed_values, lambda_value = stats.boxcox(shifted.dropna())
    transformed = pd.Series(index=shifted.index, dtype="float64")
    transformed.loc[shifted.dropna().index] = transformed_values
    return transformed, float(lambda_value)

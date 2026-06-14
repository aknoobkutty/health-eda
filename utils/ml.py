"""Machine learning helpers for classification workflows."""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


MODEL_FACTORY = {
    "Logistic Regression": lambda: LogisticRegression(max_iter=1000, class_weight="balanced"),
    "Decision Tree": lambda: DecisionTreeClassifier(random_state=42, class_weight="balanced"),
    "Random Forest": lambda: RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced_subsample"),
}


def build_preprocessor(features: pd.DataFrame) -> ColumnTransformer:
    """Create preprocessing for mixed numeric and categorical features."""
    numeric_cols = features.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [col for col in features.columns if col not in numeric_cols]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_cols),
            ("categorical", categorical_pipeline, categorical_cols),
        ],
        remainder="drop",
    )


def train_classifier(
    df: pd.DataFrame,
    target_col: str,
    model_name: str,
    test_size: float = 0.25,
) -> dict[str, object]:
    """Train and evaluate a classification model."""
    working = df.dropna(subset=[target_col]).copy()
    if working[target_col].nunique(dropna=True) < 2:
        raise ValueError("The selected target must contain at least two classes.")
    if working[target_col].nunique(dropna=True) > 50:
        raise ValueError("The selected target has too many classes for this classification dashboard.")

    y = working[target_col].astype(str)
    X = working.drop(columns=[target_col])
    X = X.drop(columns=[col for col in X.columns if X[col].nunique(dropna=True) <= 1], errors="ignore")
    if X.empty:
        raise ValueError("No usable feature columns remain after removing the target.")

    stratify = y if y.value_counts().min() >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
        stratify=stratify,
    )

    model = MODEL_FACTORY[model_name]()
    pipeline = Pipeline(steps=[("preprocessor", build_preprocessor(X)), ("model", model)])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    labels = sorted(y.unique().tolist())

    average = "binary" if len(labels) == 2 else "weighted"
    positive_label = labels[1] if len(labels) == 2 else None
    metric_kwargs = {"average": average, "zero_division": 0}
    if positive_label is not None:
        metric_kwargs["pos_label"] = positive_label

    return {
        "model": pipeline,
        "labels": labels,
        "metrics": {
            "Accuracy": accuracy_score(y_test, y_pred),
            "Precision": precision_score(y_test, y_pred, **metric_kwargs),
            "Recall": recall_score(y_test, y_pred, **metric_kwargs),
            "F1 Score": f1_score(y_test, y_pred, **metric_kwargs),
        },
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=labels),
        "test_rows": len(y_test),
        "train_rows": len(y_train),
    }

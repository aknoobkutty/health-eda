"""Machine learning page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.ml import MODEL_FACTORY, train_classifier
from utils.visualization import confusion_matrix_heatmap


def render(df: pd.DataFrame, template: str) -> None:
    """Render classification model training and evaluation."""
    st.subheader("Machine Learning")
    st.markdown(
        '<div class="insight-box">Select a target column to train a classification model. '
        "Categorical features are encoded automatically and numerical features are imputed and scaled.</div>",
        unsafe_allow_html=True,
    )

    target = st.selectbox("Target column", df.columns.tolist())
    model_name = st.selectbox("Model", list(MODEL_FACTORY.keys()))
    test_size = st.slider("Test set size", min_value=0.1, max_value=0.5, value=0.25, step=0.05)

    if st.button("Train Model", type="primary"):
        try:
            with st.spinner("Training and evaluating model..."):
                result = train_classifier(df, target, model_name, test_size)

            metrics = result["metrics"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Accuracy", f"{metrics['Accuracy']:.4f}")
            c2.metric("Precision", f"{metrics['Precision']:.4f}")
            c3.metric("Recall", f"{metrics['Recall']:.4f}")
            c4.metric("F1 Score", f"{metrics['F1 Score']:.4f}")
            st.caption(f"Train rows: {result['train_rows']:,} | Test rows: {result['test_rows']:,}")

            st.plotly_chart(
                confusion_matrix_heatmap(result["confusion_matrix"], result["labels"], template),
                use_container_width=True,
            )
        except Exception as exc:
            st.error(f"Model training failed: {exc}")

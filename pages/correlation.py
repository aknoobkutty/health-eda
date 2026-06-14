"""Correlation analysis page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.analysis import correlation_matrix, strong_correlations
from utils.data_loader import ColumnGroups
from utils.visualization import correlation_heatmap


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render correlation analysis."""
    st.subheader("Correlation Analysis")
    if len(groups.numerical) < 2:
        st.info("Correlation analysis requires at least two numerical columns.")
        return

    method = st.selectbox("Correlation method", ["pearson", "spearman", "kendall"])
    threshold = st.slider("Strong correlation threshold", 0.1, 1.0, 0.7, 0.05)
    corr = correlation_matrix(df, groups.numerical, method)

    tab_matrix, tab_strong = st.tabs(["Correlation Matrix", "Strong Relationships"])
    with tab_matrix:
        st.plotly_chart(correlation_heatmap(corr, template), use_container_width=True)
        st.dataframe(corr.round(4), use_container_width=True)
    with tab_strong:
        strong = strong_correlations(corr, threshold)
        if strong.empty:
            st.info("No strong positive or negative correlations found at the selected threshold.")
        else:
            st.dataframe(strong, use_container_width=True, hide_index=True)

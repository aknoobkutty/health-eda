"""Data quality diagnostics page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import dataframe_info
from utils.visualization import missing_values_bar, null_heatmap


def render(df: pd.DataFrame, template: str) -> None:
    """Render data quality checks."""
    st.subheader("Data Quality")

    tab_missing, tab_duplicates, tab_types = st.tabs(["Missing Values", "Duplicates", "Data Types"])

    with tab_missing:
        missing = (
            df.isna()
            .sum()
            .reset_index()
            .rename(columns={"index": "Column", 0: "Missing Count"})
        )
        missing["Missing %"] = (missing["Missing Count"] / len(df) * 100).round(2) if len(df) else 0
        missing = missing.sort_values("Missing Count", ascending=False)

        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(missing, use_container_width=True, hide_index=True)
        with c2:
            st.plotly_chart(missing_values_bar(df, template), use_container_width=True)
        with st.expander("Null Value Visualization", expanded=True):
            st.plotly_chart(null_heatmap(df, template), use_container_width=True)

    with tab_duplicates:
        duplicates = df.duplicated().sum()
        st.metric("Duplicate Rows", f"{duplicates:,}", f"{duplicates / len(df) * 100:.2f}%" if len(df) else "0%")
        if duplicates:
            st.dataframe(df[df.duplicated(keep=False)].head(200), use_container_width=True)
        else:
            st.success("No duplicate rows found.")

    with tab_types:
        st.dataframe(dataframe_info(df), use_container_width=True, hide_index=True)

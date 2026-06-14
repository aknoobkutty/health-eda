"""Outlier detection page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.analysis import iqr_outliers
from utils.data_loader import ColumnGroups
from utils.visualization import outlier_boxplot


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render IQR outlier detection."""
    st.subheader("Outlier Detection")
    if not groups.numerical:
        st.info("Outlier detection requires at least one numerical column.")
        return

    selected = st.selectbox("Numerical column", groups.numerical)
    result = iqr_outliers(df, selected)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Q1", f"{result['q1']:.4f}")
    c2.metric("Q3", f"{result['q3']:.4f}")
    c3.metric("IQR", f"{result['iqr']:.4f}")
    c4.metric("Outliers", f"{result['count']:,}", f"{result['percentage']}%")

    st.plotly_chart(outlier_boxplot(df, selected, result["lower"], result["upper"], template), use_container_width=True)
    with st.expander("Outlier Values"):
        outlier_values = result["values"].reset_index()
        outlier_values.columns = ["Row Index", selected]
        st.dataframe(outlier_values.head(500), use_container_width=True, hide_index=True)

"""Dataset upload overview page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.config import kpi_card
from utils.data_loader import ColumnGroups, dataframe_info, dataset_overview


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render dataset preview and metadata."""
    st.subheader("Dataset Overview")
    overview = dataset_overview(df)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        kpi_card("Rows", f"{overview['rows']:,}")
    with col2:
        kpi_card("Columns", f"{overview['columns']:,}")
    with col3:
        kpi_card("Missing", f"{overview['missing_pct']}%")
    with col4:
        kpi_card("Duplicates", f"{overview['duplicate_pct']}%")
    with col5:
        kpi_card("Memory", f"{overview['memory_mb']} MB")

    tab_preview, tab_info, tab_columns = st.tabs(["Preview", "Dataset Information", "Detected Columns"])

    with tab_preview:
        rows = st.slider("Rows to preview", min_value=5, max_value=min(200, max(len(df), 5)), value=min(20, max(len(df), 5)))
        st.dataframe(df.head(rows), use_container_width=True)

    with tab_info:
        info_df = dataframe_info(df)
        st.dataframe(info_df, use_container_width=True, hide_index=True)

    with tab_columns:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown("**Numerical**")
            st.write(groups.numerical or "None detected")
        with c2:
            st.markdown("**Categorical**")
            st.write(groups.categorical or "None detected")
        with c3:
            st.markdown("**Datetime-like**")
            st.write(groups.datetime or "None detected")
        with c4:
            st.markdown("**Boolean**")
            st.write(groups.boolean or "None detected")

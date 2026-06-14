"""Exploratory data analysis page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.analysis import summary_statistics
from utils.data_loader import ColumnGroups
from utils.visualization import boxplot, countplot, histogram, pie_chart, violinplot


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render automatic EDA views."""
    st.subheader("Exploratory Data Analysis")

    tab_numeric, tab_categorical, tab_summary = st.tabs(["Numerical EDA", "Categorical EDA", "Summary Statistics"])

    with tab_numeric:
        if not groups.numerical:
            st.info("No numerical columns were detected.")
        else:
            selected = st.selectbox("Numerical column", groups.numerical)
            category_options = ["None"] + groups.categorical
            selected_category = st.selectbox("Group by category", category_options)
            category = None if selected_category == "None" else selected_category

            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(histogram(df, selected, template), use_container_width=True)
                st.plotly_chart(violinplot(df, selected, category, template), use_container_width=True)
            with c2:
                st.plotly_chart(boxplot(df, selected, category, template), use_container_width=True)

    with tab_categorical:
        if not groups.categorical:
            st.info("No categorical columns were detected.")
        else:
            selected = st.selectbox("Categorical column", groups.categorical)
            c1, c2 = st.columns(2)
            with c1:
                st.plotly_chart(countplot(df, selected, template), use_container_width=True)
            with c2:
                st.plotly_chart(pie_chart(df, selected, template), use_container_width=True)

    with tab_summary:
        numeric_summary, categorical_summary = summary_statistics(df, groups.numerical, groups.categorical)
        st.markdown("**Numerical Summary**")
        if numeric_summary.empty:
            st.info("No numerical summary available.")
        else:
            st.dataframe(numeric_summary, use_container_width=True)
        st.markdown("**Categorical Summary**")
        if categorical_summary.empty:
            st.info("No categorical summary available.")
        else:
            st.dataframe(categorical_summary, use_container_width=True, hide_index=True)

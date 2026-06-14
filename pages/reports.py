"""Report generation page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.data_loader import ColumnGroups
from utils.reporting import build_csv_summary, build_insights, build_pdf_report


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render report downloads."""
    st.subheader("Report Generation")

    insights = build_insights(df, groups.numerical, groups.categorical)
    st.markdown("**Generated Insights**")
    for insight in insights:
        st.markdown(f"- {insight}")

    text_report = "\n".join(f"- {insight}" for insight in insights)
    csv_summary = build_csv_summary(df, groups.numerical, groups.categorical)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download Insights",
            data=text_report.encode("utf-8"),
            file_name="eda_insights.txt",
            mime="text/plain",
        )
    with col2:
        st.download_button(
            "Download CSV Summary",
            data=csv_summary.encode("utf-8"),
            file_name="eda_summary.csv",
            mime="text/csv",
        )
    with col3:
        pdf = build_pdf_report(df, groups.numerical, groups.categorical)
        st.download_button(
            "Download PDF Report",
            data=pdf,
            file_name="eda_report.pdf",
            mime="application/pdf",
        )

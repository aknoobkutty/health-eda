"""Data transformation page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.analysis import boxcox_transform, log_transform
from utils.data_loader import ColumnGroups
from utils.visualization import histogram


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render transformation tools."""
    st.subheader("Data Transformation")
    if not groups.numerical:
        st.info("Data transformation requires at least one numerical column.")
        return

    selected = st.selectbox("Numerical column", groups.numerical)
    method = st.radio("Transformation", ["Log Transformation", "Box-Cox Transformation"], horizontal=True)

    transformed_df = df.copy()
    output_col = f"{selected}_{'log' if method.startswith('Log') else 'boxcox'}"

    try:
        if method == "Log Transformation":
            transformed_df[output_col] = log_transform(df[selected])
            st.success(f"Created transformed column: {output_col}")
        else:
            transformed_df[output_col], lambda_value = boxcox_transform(df[selected])
            st.success(f"Created transformed column: {output_col} with lambda = {lambda_value:.4f}")

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(histogram(df, selected, template), use_container_width=True)
        with c2:
            st.plotly_chart(histogram(transformed_df, output_col, template), use_container_width=True)

        csv = transformed_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Transformed Dataset", data=csv, file_name="transformed_dataset.csv", mime="text/csv")
    except Exception as exc:
        st.warning(f"Unable to apply transformation: {exc}")

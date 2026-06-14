"""Universal Streamlit EDA Dashboard."""

from __future__ import annotations

import streamlit as st

from pages import (
    correlation,
    data_quality,
    eda,
    healthcare_mode,
    machine_learning,
    outliers,
    overview,
    reports,
    statistical_analysis,
    transformation,
)
from utils.config import (
    APP_SUBTITLE,
    APP_TITLE,
    configure_page,
    inject_css,
    loaded_dataset_card,
    plotly_template,
    sidebar_brand,
    sidebar_section,
)
from utils.data_loader import infer_column_groups, normalize_column_names, read_csv
from utils.healthcare import detect_no_show_dataset


PAGES = {
    "Overview": overview.render,
    "Data Quality": data_quality.render,
    "Univariate Analysis": eda.render,
    "Bivariate Analysis": correlation.render,
    "Correlation Analysis": correlation.render,
    "Statistical Tests": statistical_analysis.render,
    "Healthcare Insights": healthcare_mode.render,
    "Machine Learning": machine_learning.render,
    "Report Generation": reports.render,
    "Outlier Detection": outliers.render,
    "Data Transformation": transformation.render,
}


def render_header() -> None:
    """Render the dashboard title."""
    st.markdown(
        f"""
        <div class="app-topbar">
            <div class="topbar-left">
                <div class="dashboard-title">
                    <h1>{APP_TITLE}</h1>
                    <p>{APP_SUBTITLE}</p>
                </div>
            </div>
            <div class="topbar-actions">
                <div class="user-pill"><div class="avatar"></div>Admin User</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_state() -> None:
    """Render the empty state before a dataset is uploaded."""
    st.info("Upload a CSV file from the left panel to start automated EDA.")
    with st.expander("What this dashboard will analyze", expanded=True):
        st.markdown(
            """
            - Dataset preview and inferred column types
            - Missing values, duplicates, data types, and null maps
            - Histograms, boxplots, violin plots, count plots, pie charts, and summary statistics
            - Correlation heatmaps with strong positive and negative relationships
            - Chi-Square tests, ANOVA, skewness, kurtosis, and normality checks
            - IQR outlier detection and transformation downloads
            - Classification models with accuracy, precision, recall, F1, and confusion matrix
            - PDF, CSV, and text insight downloads
            - Automatic healthcare no-show analysis when the matching schema is detected
            """
        )


def main() -> None:
    """Run the Streamlit application."""
    configure_page()
    theme = st.session_state.get("theme", "Light")
    inject_css(theme)
    template = plotly_template(theme)

    side_panel, content = st.columns([0.18, 0.82], gap="large")

    with side_panel:
        sidebar_brand()
        sidebar_section("Upload Dataset")
        uploaded_file = st.file_uploader("Upload CSV dataset", type=["csv"])
        sidebar_section("Settings")
        st.radio("Theme", ["Light", "Dark"], horizontal=True, key="theme")
        st.divider()

        sidebar_section("Main Menu")
        page_name = st.radio("Navigate", list(PAGES.keys()), label_visibility="visible")

    with content:
        render_header()

        if uploaded_file is None:
            render_upload_state()
            return

        try:
            df = normalize_column_names(read_csv(uploaded_file))
        except Exception as exc:
            st.error(f"Could not read the uploaded CSV: {exc}")
            return

        if df.empty:
            st.warning("The uploaded CSV is empty.")
            return

        groups = infer_column_groups(df)
        healthcare_detected = detect_no_show_dataset(df)

    with side_panel:
        sidebar_section("Dataset Status")
        loaded_dataset_card(uploaded_file.name, df.shape[0], df.shape[1])
        if healthcare_detected:
            st.caption("Healthcare no-show schema detected.")

    with content:
        if page_name == "Machine Learning":
            PAGES[page_name](df, template)
        elif page_name == "Data Quality":
            PAGES[page_name](df, template)
        elif page_name == "Healthcare Insights":
            PAGES[page_name](df, template)
        else:
            PAGES[page_name](df, groups, template)


if __name__ == "__main__":
    main()

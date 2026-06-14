"""Statistical analysis page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.analysis import anova_test, chi_square_test, distribution_tests
from utils.data_loader import ColumnGroups


def _format_p_value(p_value: float) -> str:
    return "< 0.000001" if p_value < 0.000001 else f"{p_value:.6f}"


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render statistical tests."""
    st.subheader("Statistical Analysis")

    tab_distribution, tab_chi, tab_anova = st.tabs(["Skewness, Kurtosis, Normality", "Chi-Square Test", "ANOVA"])

    with tab_distribution:
        results = distribution_tests(df, groups.numerical)
        if results.empty:
            st.info("Distribution tests require numerical columns with at least three non-null values.")
        else:
            st.dataframe(results, use_container_width=True, hide_index=True)

    with tab_chi:
        if len(groups.categorical) < 2:
            st.info("Chi-Square test requires at least two categorical columns.")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                first = st.selectbox("First categorical column", groups.categorical, key="chi_first")
            with col_b:
                second_options = [col for col in groups.categorical if col != first]
                second = st.selectbox("Second categorical column", second_options, key="chi_second")
            try:
                result = chi_square_test(df, first, second)
                st.metric("Chi-Square Statistic", f"{result['chi2']:.4f}")
                st.metric("p-value", _format_p_value(result["p_value"]))
                st.write(f"Degrees of freedom: {result['degrees_of_freedom']}")
                st.caption("A p-value below 0.05 suggests the two categorical variables are not independent.")
            except Exception as exc:
                st.warning(f"Unable to run Chi-Square test: {exc}")

    with tab_anova:
        if not groups.categorical or not groups.numerical:
            st.info("ANOVA requires one categorical column and one numerical column.")
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                category = st.selectbox("Group column", groups.categorical, key="anova_cat")
            with col_b:
                numeric = st.selectbox("Numeric outcome", groups.numerical, key="anova_num")
            try:
                result = anova_test(df, category, numeric)
                st.metric("F Statistic", f"{result['f_statistic']:.4f}")
                st.metric("p-value", _format_p_value(result["p_value"]))
                st.write(f"Groups tested: {result['groups_tested']}")
                st.caption("A p-value below 0.05 suggests at least one group mean differs.")
            except Exception as exc:
                st.warning(f"Unable to run ANOVA: {exc}")

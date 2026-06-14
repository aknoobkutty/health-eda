"""Dataset upload overview page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.config import kpi_card, med_kpi_card
from utils.data_loader import ColumnGroups, dataframe_info, dataset_overview
from utils.healthcare import (
    detect_no_show_dataset,
    doctor_allocation_recommendations,
    grouped_no_show_rate,
    no_show_summary,
    prepare_no_show_data,
)


def _column_lookup(df: pd.DataFrame, *candidates: str) -> str | None:
    normalized = {str(col).lower().replace("_", "").replace("-", ""): col for col in df.columns}
    for candidate in candidates:
        key = candidate.lower().replace("_", "").replace("-", "")
        if key in normalized:
            return normalized[key]
    return None


def _compact_number(value: float | int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:,.0f}"


def _line_spark(values: pd.Series, color: str, template: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            y=values,
            mode="lines",
            line=dict(color=color, width=2.4),
            fill="tozeroy",
            fillcolor=color.replace(")", ", 0.12)").replace("rgb", "rgba") if color.startswith("rgb") else "rgba(79, 99, 246, 0.12)",
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        template=template,
        height=70,
        margin=dict(l=0, r=0, t=8, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _donut(labels: list[str], values: list[int], colors: list[str], template: str) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.58,
                marker=dict(colors=colors),
                textinfo="none",
            )
        ]
    )
    fig.update_layout(
        template=template,
        height=270,
        margin=dict(l=0, r=0, t=5, b=0),
        legend=dict(orientation="v", x=0.78, y=0.5),
        annotations=[
            dict(
                text=f"{sum(values):,}<br><span style='font-size:12px'>Total</span>",
                x=0.34,
                y=0.5,
                showarrow=False,
                font=dict(size=20),
            )
        ],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def _render_card_start(title: str) -> None:
    st.markdown(f'<div class="plot-card"><div class="card-title">{title}</div>', unsafe_allow_html=True)


def _render_card_end() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def _render_healthcare_overview(df: pd.DataFrame, template: str) -> None:
    data = prepare_no_show_data(df)
    summary = no_show_summary(df)
    patient_col = _column_lookup(data, "PatientId", "Patient ID")
    gender_col = _column_lookup(data, "Gender")
    neighbourhood_col = _column_lookup(data, "Neighbourhood", "Neighborhood")
    hypertension_col = _column_lookup(data, "Hipertension", "Hypertension")
    diabetes_col = _column_lookup(data, "Diabetes")
    alcoholism_col = _column_lookup(data, "Alcoholism")
    scholarship_col = _column_lookup(data, "Scholarship")
    handicap_col = _column_lookup(data, "Handcap", "Handicap")

    unique_patients = data[patient_col].nunique(dropna=True) if patient_col else len(data)
    no_show_count = int(data["NoShowFlag"].sum()) if "NoShowFlag" in data else 0
    show_count = int(len(data) - no_show_count)
    sms_count = int(data["SMSReceived"].sum()) if "SMSReceived" in data else 0

    st.download_button(
        "Download Report",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="healthcare_dashboard_dataset.csv",
        mime="text/csv",
        use_container_width=False,
    )

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        med_kpi_card("Total Appointments", f"{summary['appointments']:,}", "Total Records", "soft-purple", "#6d5dfc")
        st.plotly_chart(_line_spark(pd.Series(range(15)).rolling(3, min_periods=1).mean(), "#6d5dfc", template), use_container_width=True)
    with k2:
        med_kpi_card("No-Show Rate", f"{summary['no_show_rate']}%", f"{no_show_count:,} No-Shows", "soft-blue", "#3b82f6")
    with k3:
        med_kpi_card("Avg Waiting Time", f"{summary['avg_waiting_days']}", "Days", "soft-green", "#10b981")
    with k4:
        med_kpi_card("SMS Sent Rate", f"{summary['sms_rate']}%", f"{sms_count:,} SMS Sent", "soft-yellow", "#f59e0b")
    with k5:
        med_kpi_card("Unique Patients", f"{unique_patients:,}", "Patients", "soft-pink", "#ec4899")

    left, middle, right = st.columns([1.65, 1.35, 1])
    with left:
        _render_card_start("Appointments Over Time")
        if "AppointmentDate" in data:
            by_month = data.dropna(subset=["AppointmentDate"]).set_index("AppointmentDate").resample("ME").size().reset_index(name="Appointments")
            fig = px.line(by_month, x="AppointmentDate", y="Appointments", markers=True, template=template)
            fig.update_traces(line_color="#3b82f6", fill="tozeroy", fillcolor="rgba(59,130,246,0.12)")
            fig.update_layout(height=285, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Appointment date column was not found.")
        _render_card_end()
    with middle:
        _render_card_start("No-Show Distribution")
        st.plotly_chart(_donut(["Showed Up", "No-Show"], [show_count, no_show_count], ["#41c997", "#f84f7f"], template), use_container_width=True)
        _render_card_end()
    with right:
        _render_card_start("Dataset Information")
        overview = dataset_overview(df)
        info_rows = [
            ("Rows", f"{overview['rows']:,}"),
            ("Columns", f"{overview['columns']:,}"),
            ("Missing Values", f"{overview['missing_cells']:,} ({overview['missing_pct']}%)"),
            ("Duplicate Rows", f"{overview['duplicate_rows']:,} ({overview['duplicate_pct']}%)"),
            ("Memory Usage", f"{overview['memory_mb']} MB"),
            ("Last Updated", pd.Timestamp.now().strftime("%b %d, %Y %I:%M %p")),
        ]
        for label, value in info_rows:
            st.markdown(f'<div class="quick-action"><span>{label}</span><span>{value}</span></div>', unsafe_allow_html=True)
        _render_card_end()

    bottom_left, bottom_mid, bottom_bar, bottom_right = st.columns([1.25, 1.18, 1.35, 1])
    with bottom_left:
        _render_card_start("Age Distribution")
        if "AgeClean" in data:
            fig = px.histogram(data, x="AgeClean", nbins=35, marginal=None, template=template)
            fig.update_traces(marker_color="#7c5cff", opacity=0.85)
            fig.update_layout(height=285, margin=dict(l=8, r=8, t=8, b=8), xaxis_title="Age", yaxis_title="Count", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        _render_card_end()
    with bottom_mid:
        _render_card_start("Gender Distribution")
        if gender_col:
            gender_counts = data[gender_col].fillna("Missing").value_counts()
            fig = _donut(gender_counts.index.astype(str).tolist(), gender_counts.astype(int).tolist(), ["#f472b6", "#60a5fa", "#94a3b8"], template)
            st.plotly_chart(fig, use_container_width=True)
        _render_card_end()
    with bottom_bar:
        _render_card_start("Top 10 Neighborhoods")
        if neighbourhood_col:
            top_neighbourhoods = data[neighbourhood_col].value_counts().head(10).sort_values()
            fig = px.bar(
                x=top_neighbourhoods.values,
                y=top_neighbourhoods.index,
                orientation="h",
                template=template,
                text=top_neighbourhoods.values,
            )
            fig.update_traces(marker_color="#4f63f6", textposition="outside")
            fig.update_layout(height=285, margin=dict(l=8, r=28, t=8, b=8), xaxis_title="", yaxis_title="", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
        _render_card_end()
    with bottom_right:
        _render_card_start("Quick Actions")
        actions = ["View Missing Values", "Detect Outliers", "Run Correlation", "Statistical Tests", "Train ML Model", "Generate Report"]
        for action in actions:
            st.markdown(f'<div class="quick-action"><span>{action}</span><span>&gt;</span></div>', unsafe_allow_html=True)
        _render_card_end()

    strip_cols = st.columns(5)
    health_fields = [
        ("Hypertension", hypertension_col, "H"),
        ("Diabetes", diabetes_col, "D"),
        ("Alcoholism", alcoholism_col, "A"),
        ("Scholarship", scholarship_col, "S"),
        ("Handicap", handicap_col, "C"),
    ]
    for col, (label, source_col, short) in zip(strip_cols, health_fields):
        with col:
            if source_col:
                pct = pd.to_numeric(data[source_col], errors="coerce").fillna(0).mean() * 100
                value = f"{pct:.2f}%"
            else:
                value = "N/A"
            st.markdown(
                f"""
                <div class="health-strip">
                    <div class="health-item">
                        <div class="health-dot soft-pink">{short}</div>
                        <div>
                            <div class="small-muted">{label}</div>
                            <div class="kpi-value" style="font-size:1.28rem;">{value}</div>
                            <div class="small-muted">Patients</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    insight_left, insight_right = st.columns([2.2, 1])
    with insight_left:
        recommendations = doctor_allocation_recommendations(data)
        with st.expander("Doctor Allocation Recommendations", expanded=False):
            if recommendations.empty:
                st.info("Recommendations require neighbourhood and no-show columns.")
            else:
                st.dataframe(recommendations.head(20), use_container_width=True, hide_index=True)
    with insight_right:
        st.markdown(
            f"""
            <div class="ai-box">
                <div class="card-title">AI Insight</div>
                <div>No-show rate is {summary['no_show_rate']}%. SMS reminders and shorter waiting windows are the highest-impact operational levers.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render(df: pd.DataFrame, groups: ColumnGroups, template: str) -> None:
    """Render dataset preview and metadata."""
    if detect_no_show_dataset(df):
        _render_healthcare_overview(df, template)
        return

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

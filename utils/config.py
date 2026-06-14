"""Application configuration and UI helpers."""

from __future__ import annotations

import streamlit as st


APP_TITLE = "Universal EDA Dashboard"
APP_SUBTITLE = "Automated exploratory analysis, modeling, and reporting for any CSV dataset."


def configure_page() -> None:
    """Configure the Streamlit page once at startup."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_css(theme: str = "Light") -> None:
    """Inject compact dashboard styling for light or dark mode."""
    dark = theme.lower() == "dark"
    colors = {
        "bg": "#0f172a" if dark else "#f8fafc",
        "panel": "#111827" if dark else "#ffffff",
        "muted_panel": "#1f2937" if dark else "#eef2ff",
        "text": "#f8fafc" if dark else "#0f172a",
        "muted": "#cbd5e1" if dark else "#475569",
        "border": "#334155" if dark else "#e2e8f0",
        "accent": "#38bdf8" if dark else "#2563eb",
        "accent_soft": "#0c4a6e" if dark else "#dbeafe",
        "good": "#22c55e",
        "warn": "#f59e0b",
        "bad": "#ef4444",
    }

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {colors["bg"]};
            color: {colors["text"]};
        }}
        [data-testid="stSidebar"] {{
            background: {colors["panel"]};
            border-right: 1px solid {colors["border"]};
        }}
        [data-testid="stMetric"] {{
            background: {colors["panel"]};
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            padding: 14px 16px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
        }}
        .dashboard-title {{
            padding: 0.25rem 0 1rem 0;
        }}
        .dashboard-title h1 {{
            color: {colors["text"]};
            font-size: 2rem;
            line-height: 1.2;
            margin-bottom: 0.25rem;
        }}
        .dashboard-title p {{
            color: {colors["muted"]};
            margin: 0;
            font-size: 1rem;
        }}
        .kpi-card {{
            background: {colors["panel"]};
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            padding: 14px 16px;
            min-height: 96px;
        }}
        .kpi-label {{
            color: {colors["muted"]};
            font-size: 0.86rem;
            margin-bottom: 0.25rem;
        }}
        .kpi-value {{
            color: {colors["text"]};
            font-size: 1.55rem;
            font-weight: 700;
        }}
        .insight-box {{
            background: {colors["accent_soft"]};
            border-left: 4px solid {colors["accent"]};
            border-radius: 6px;
            padding: 12px 14px;
            color: {colors["text"]};
            margin: 0.5rem 0 1rem 0;
        }}
        .small-muted {{
            color: {colors["muted"]};
            font-size: 0.9rem;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {colors["border"]};
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, help_text: str | None = None) -> None:
    """Render a small KPI card with consistent styling."""
    help_html = f'<div class="small-muted">{help_text}</div>' if help_text else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_template(theme: str = "Light") -> str:
    """Return a Plotly template matching the selected theme."""
    return "plotly_dark" if theme.lower() == "dark" else "plotly_white"

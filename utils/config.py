"""Application configuration and UI helpers."""

from __future__ import annotations

import streamlit as st


APP_TITLE = "Healthcare EDA Dashboard"
APP_SUBTITLE = "Exploratory Data Analysis & Healthcare Insights"


def configure_page() -> None:
    """Configure the Streamlit page once at startup."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=":bar_chart:",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_css(theme: str = "Light") -> None:
    """Inject dashboard styling for light or dark mode."""
    dark = theme.lower() == "dark"
    colors = {
        "bg": "#08111f" if dark else "#f8fbff",
        "panel": "#101b2e" if dark else "#ffffff",
        "panel_2": "#0d1728" if dark else "#f8fbff",
        "text": "#eef6ff" if dark else "#071a3a",
        "muted": "#9fb0c8" if dark else "#60708b",
        "border": "#1e334f" if dark else "#dfe7f2",
        "accent": "#5b6cff" if dark else "#4f63f6",
        "accent_2": "#7c3aed" if dark else "#6d5dfc",
        "sidebar_1": "#021b33",
        "sidebar_2": "#051124",
        "soft_blue": "#122b54" if dark else "#edf4ff",
        "soft_purple": "#22184a" if dark else "#f5f1ff",
        "soft_green": "#0b3a2d" if dark else "#ecfbf4",
        "soft_yellow": "#3d2d06" if dark else "#fff8e8",
        "soft_pink": "#3b1428" if dark else "#fff0f7",
        "good": "#22c55e",
        "warn": "#f59e0b",
        "bad": "#ef4444",
    }

    st.markdown(
        f"""
        <style>
        :root {{
            --app-bg: {colors["bg"]};
            --panel-bg: {colors["panel"]};
            --panel-bg-2: {colors["panel_2"]};
            --text-main: {colors["text"]};
            --text-muted: {colors["muted"]};
            --border-soft: {colors["border"]};
            --accent-main: {colors["accent"]};
        }}
        html, body, .stApp {{
            background: {colors["bg"]};
            color: {colors["text"]};
        }}
        [data-testid="stHeader"] {{
            background: transparent;
            height: 3rem;
        }}
        [data-testid="stToolbar"] {{
            display: none;
        }}
        [data-testid="stSidebarCollapseButton"],
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }}
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {{
            position: fixed !important;
            top: 0.8rem !important;
            left: 0.8rem !important;
            width: 42px !important;
            height: 42px !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 10px !important;
            background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%) !important;
            box-shadow: 0 12px 28px rgba(37, 99, 235, 0.28) !important;
        }}
        [data-testid="stSidebarCollapseButton"] button,
        [data-testid="stSidebarCollapseButton"] svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}
        [data-testid="stSidebarCollapsedControl"] button,
        [data-testid="stSidebarCollapsedControl"] svg,
        [data-testid="collapsedControl"] button,
        [data-testid="collapsedControl"] svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}
        .block-container {{
            padding: 1.1rem 1.6rem 2.5rem 1.6rem;
            max-width: 1500px;
        }}
        [data-testid="stAppViewContainer"] .block-container > div > div > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child {{
            background: linear-gradient(180deg, {colors["sidebar_1"]} 0%, {colors["sidebar_2"]} 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 0;
            padding: 1rem 0.9rem;
            min-height: calc(100vh - 2.2rem);
            position: sticky;
            top: 1rem;
            align-self: flex-start;
        }}
        [data-testid="stAppViewContainer"] .block-container > div > div > div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child * {{
            color: #eff6ff;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {colors["sidebar_1"]} 0%, {colors["sidebar_2"]} 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
            min-width: 260px;
            max-width: 260px;
        }}
        [data-testid="stSidebarNav"],
        [data-testid="stSidebarNavItems"],
        section[data-testid="stSidebar"] nav {{
            display: none !important;
            height: 0 !important;
            visibility: hidden !important;
        }}
        [data-testid="stSidebar"] * {{
            color: #eff6ff;
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {{
            color: #eff6ff !important;
        }}
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {{
            background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
            border: 0;
            border-radius: 10px;
            color: #ffffff;
        }}
        [data-testid="stFileUploaderDropzone"] {{
            background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%) !important;
            border: 0 !important;
            border-radius: 10px !important;
            color: #ffffff !important;
        }}
        [data-testid="stFileUploaderDropzone"] button,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.35) !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            font-weight: 800 !important;
            box-shadow: 0 10px 24px rgba(5, 150, 105, 0.28) !important;
        }}
        [data-testid="stFileUploaderDropzone"] button:hover,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {{
            background: linear-gradient(135deg, #34d399 0%, #10b981 100%) !important;
            color: #ffffff !important;
        }}
        [data-testid="stFileUploaderDropzone"] svg,
        [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label {{
            border-radius: 10px;
            padding: 0.45rem 0.55rem;
            margin-bottom: 0.2rem;
        }}
        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{
            background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.24);
        }}
        [data-testid="stSidebar"] hr {{
            border-color: rgba(255, 255, 255, 0.09);
        }}
        [data-testid="stMetric"] {{
            background: {colors["panel"]};
            border: 1px solid {colors["border"]};
            border-radius: 12px;
            padding: 14px 16px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        }}
        [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{
            color: {colors["text"]} !important;
        }}
        h1, h2, h3, h4, h5, h6, p, label, span, div {{
            color: inherit;
        }}
        .app-topbar {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin: -0.25rem 0 1.3rem 0;
            padding: 0 0 1rem 0;
            border-bottom: 1px solid {colors["border"]};
        }}
        .topbar-left {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .hamburger {{
            font-size: 1.6rem;
            color: {colors["text"]};
            line-height: 1;
        }}
        .dashboard-title h1 {{
            color: {colors["text"]};
            font-size: 1.62rem;
            line-height: 1.2;
            margin: 0 0 0.18rem 0;
            font-weight: 800;
        }}
        .dashboard-title p {{
            color: {colors["muted"]};
            margin: 0;
            font-size: 0.98rem;
        }}
        .topbar-actions {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            color: {colors["text"]};
            font-size: 1.15rem;
        }}
        .user-pill {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
            border: 1px solid {colors["border"]};
            border-radius: 12px;
            padding: 0.45rem 0.75rem;
            background: {colors["panel"]};
            color: {colors["text"]};
            font-weight: 600;
            font-size: 0.92rem;
        }}
        .avatar {{
            width: 30px;
            height: 30px;
            border-radius: 999px;
            background: linear-gradient(135deg, #f472b6, #60a5fa);
        }}
        .sidebar-brand {{
            display: flex;
            gap: 0.75rem;
            align-items: center;
            padding: 1.2rem 0.4rem 1.35rem 0.4rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
            margin-bottom: 1rem;
        }}
        .brand-mark {{
            width: 43px;
            height: 43px;
            border-radius: 14px;
            background: linear-gradient(135deg, #ff3f78 0%, #f43f5e 55%, #7c3aed 100%);
            display: grid;
            place-items: center;
            color: #ffffff;
            font-weight: 900;
            font-size: 1.22rem;
            box-shadow: 0 18px 35px rgba(244, 63, 94, 0.3);
        }}
        .brand-name {{
            font-size: 1.34rem;
            font-weight: 800;
            color: #ffffff;
            line-height: 1.1;
        }}
        .brand-subtitle {{
            color: #9fb0c8;
            font-size: 0.86rem;
            margin-top: 0.12rem;
        }}
        .sidebar-section {{
            margin: 1rem 0 0.5rem 0.35rem;
            color: #8aa2bf;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .loaded-card {{
            background: linear-gradient(135deg, #3857ea 0%, #635bff 100%);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 10px;
            padding: 0.9rem 1rem;
            color: #ffffff;
            margin-top: 1rem;
            box-shadow: 0 16px 38px rgba(59, 91, 255, 0.22);
        }}
        .loaded-card .loaded-title {{
            font-weight: 800;
            margin-bottom: 0.55rem;
        }}
        .loaded-card .loaded-line {{
            color: #dfe7ff;
            font-size: 0.85rem;
            margin: 0.2rem 0;
        }}
        .kpi-card {{
            background: {colors["panel"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 18px 20px;
            min-height: 118px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
            position: relative;
            overflow: hidden;
        }}
        .kpi-label {{
            color: {colors["text"]};
            font-size: 0.92rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }}
        .kpi-value {{
            color: {colors["text"]};
            font-size: 1.68rem;
            font-weight: 850;
            line-height: 1.1;
        }}
        .kpi-help {{
            color: {colors["muted"]};
            margin-top: 0.45rem;
            font-size: 0.9rem;
        }}
        .med-card {{
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            background: {colors["panel"]};
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
            padding: 1rem;
            min-height: 100%;
        }}
        .card-title {{
            color: {colors["text"]};
            font-weight: 800;
            font-size: 1rem;
            margin-bottom: 0.7rem;
        }}
        .quick-action {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border: 1px solid {colors["border"]};
            border-radius: 9px;
            padding: 0.62rem 0.72rem;
            margin: 0.48rem 0;
            background: {colors["panel_2"]};
            color: {colors["text"]};
            font-weight: 650;
            font-size: 0.9rem;
        }}
        .ai-box {{
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.16), rgba(20, 184, 166, 0.08));
            border: 1px solid rgba(16, 185, 129, 0.22);
            border-radius: 10px;
            padding: 1rem;
            color: {colors["text"]};
        }}
        .health-strip {{
            background: {colors["panel"]};
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            padding: 0.9rem 1rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }}
        .health-item {{
            display: flex;
            align-items: center;
            gap: 0.8rem;
            border-right: 1px solid {colors["border"]};
        }}
        .health-item:last-child {{
            border-right: 0;
        }}
        .health-dot {{
            width: 42px;
            height: 42px;
            border-radius: 999px;
            display: grid;
            place-items: center;
            font-weight: 800;
        }}
        .soft-blue {{ background: {colors["soft_blue"]}; }}
        .soft-purple {{ background: {colors["soft_purple"]}; }}
        .soft-green {{ background: {colors["soft_green"]}; }}
        .soft-yellow {{ background: {colors["soft_yellow"]}; }}
        .soft-pink {{ background: {colors["soft_pink"]}; }}
        .plot-card {{
            border: 1px solid {colors["border"]};
            border-radius: 10px;
            background: {colors["panel"]};
            padding: 1rem;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.07);
        }}
        .insight-box {{
            background: {colors["soft_blue"]};
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
        div[data-testid="stTabs"] button {{
            color: {colors["muted"]};
        }}
        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: {colors["accent"]};
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            overflow: hidden;
        }}
        div[data-testid="stDataFrame"] * {{
            color: {colors["text"]};
        }}
        .stSlider [data-baseweb="slider"] > div {{
            color: {colors["accent"]};
        }}
        .stButton button,
        .stDownloadButton button {{
            border-radius: 9px;
            border: 1px solid {colors["border"]};
            background: linear-gradient(135deg, #4f63f6 0%, #6d5dfc 100%);
            color: #ffffff;
            font-weight: 750;
        }}
        .stSelectbox [data-baseweb="select"],
        .stTextInput input,
        .stNumberInput input {{
            background: {colors["panel"]};
            border-color: {colors["border"]};
            color: {colors["text"]};
        }}
        @media (max-width: 900px) {{
            .block-container {{
                padding: 1rem;
            }}
            .app-topbar {{
                align-items: flex-start;
                flex-direction: column;
            }}
            .topbar-actions {{
                width: 100%;
                justify-content: space-between;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, help_text: str | None = None) -> None:
    """Render a small KPI card with consistent styling."""
    help_html = f'<div class="kpi-help">{help_text}</div>' if help_text else ""
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


def med_kpi_card(
    title: str,
    value: str,
    subtitle: str,
    tone: str = "soft-blue",
    accent: str = "#4f63f6",
) -> None:
    """Render a reference-style KPI card."""
    st.markdown(
        f"""
        <div class="kpi-card {tone}">
            <div style="display:flex; gap:1rem; align-items:flex-start;">
                <div class="health-dot" style="background: rgba(255,255,255,0.42); color:{accent};">{title[:1]}</div>
                <div>
                    <div class="kpi-label">{title}</div>
                    <div class="kpi-value">{value}</div>
                    <div class="kpi-help">{subtitle}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_brand() -> None:
    """Render the MedInsight sidebar brand."""
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-mark">M</div>
            <div>
                <div class="brand-name">MedInsight</div>
                <div class="brand-subtitle">Analytics</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_section(label: str) -> None:
    """Render a sidebar section label."""
    st.markdown(f'<div class="sidebar-section">{label}</div>', unsafe_allow_html=True)


def loaded_dataset_card(filename: str, rows: int, columns: int) -> None:
    """Render the sidebar loaded dataset card."""
    st.markdown(
        f"""
        <div class="loaded-card">
            <div class="loaded-title">Dataset Loaded</div>
            <div class="loaded-line">{filename}</div>
            <div class="loaded-line">{rows:,} rows - {columns:,} columns</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plotly_template(theme: str = "Light") -> str:
    """Return a Plotly template matching the selected theme."""
    return "plotly_dark" if theme.lower() == "dark" else "plotly_white"

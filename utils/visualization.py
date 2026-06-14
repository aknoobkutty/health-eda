"""Plotly visualization helpers for dashboard pages."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go


def missing_values_bar(df: pd.DataFrame, template: str) -> go.Figure:
    missing = (
        df.isna()
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"index": "Column", 0: "Missing"})
    )
    missing["Missing %"] = (missing["Missing"] / len(df) * 100).round(2) if len(df) else 0
    fig = px.bar(
        missing.head(30),
        x="Column",
        y="Missing",
        color="Missing %",
        title="Missing Values by Column",
        template=template,
        color_continuous_scale="Blues",
    )
    fig.update_layout(xaxis_tickangle=-35, height=420)
    return fig


def null_heatmap(df: pd.DataFrame, template: str, max_rows: int = 500) -> go.Figure:
    sample = df.head(max_rows).isna().astype(int)
    fig = px.imshow(
        sample.T,
        aspect="auto",
        color_continuous_scale=[[0, "#e2e8f0"], [1, "#ef4444"]],
        labels=dict(x="Row", y="Column", color="Null"),
        title=f"Null Value Map (first {min(max_rows, len(df)):,} rows)",
        template=template,
    )
    fig.update_layout(height=max(360, min(720, 22 * len(sample.columns))))
    return fig


def histogram(df: pd.DataFrame, column: str, template: str) -> go.Figure:
    fig = px.histogram(df, x=column, marginal="box", nbins=40, template=template, title=f"Histogram: {column}")
    fig.update_layout(height=430)
    return fig


def boxplot(df: pd.DataFrame, column: str, category: str | None, template: str) -> go.Figure:
    fig = px.box(
        df,
        x=category if category else None,
        y=column,
        points="outliers",
        template=template,
        title=f"Boxplot: {column}" + (f" by {category}" if category else ""),
    )
    fig.update_layout(height=430)
    return fig


def violinplot(df: pd.DataFrame, column: str, category: str | None, template: str) -> go.Figure:
    fig = px.violin(
        df,
        x=category if category else None,
        y=column,
        box=True,
        points=False,
        template=template,
        title=f"Violin Plot: {column}" + (f" by {category}" if category else ""),
    )
    fig.update_layout(height=430)
    return fig


def countplot(df: pd.DataFrame, column: str, template: str, top_n: int = 25) -> go.Figure:
    counts = df[column].astype("object").fillna("Missing").value_counts().head(top_n).reset_index()
    counts.columns = [column, "Count"]
    fig = px.bar(counts, x=column, y="Count", template=template, title=f"Count Plot: {column}")
    fig.update_layout(xaxis_tickangle=-35, height=430)
    return fig


def pie_chart(df: pd.DataFrame, column: str, template: str, top_n: int = 10) -> go.Figure:
    values = df[column].astype("object").fillna("Missing").value_counts()
    top = values.head(top_n)
    if len(values) > top_n:
        top.loc["Other"] = values.iloc[top_n:].sum()
    plot_df = top.reset_index()
    plot_df.columns = [column, "Count"]
    fig = px.pie(plot_df, names=column, values="Count", template=template, title=f"Pie Chart: {column}")
    fig.update_layout(height=430)
    return fig


def correlation_heatmap(corr: pd.DataFrame, template: str) -> go.Figure:
    fig = px.imshow(
        corr,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        template=template,
        title="Correlation Heatmap",
    )
    fig.update_layout(height=max(480, min(900, 28 * len(corr.columns))))
    return fig


def confusion_matrix_heatmap(matrix: np.ndarray, labels: list[str], template: str) -> go.Figure:
    fig = ff.create_annotated_heatmap(
        z=matrix,
        x=labels,
        y=labels,
        colorscale="Blues",
        showscale=True,
    )
    fig.update_layout(
        title="Confusion Matrix",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        template=template,
        height=480,
    )
    return fig


def outlier_boxplot(df: pd.DataFrame, column: str, lower: float, upper: float, template: str) -> go.Figure:
    plot_df = df[[column]].copy()
    plot_df["Outlier"] = np.where((plot_df[column] < lower) | (plot_df[column] > upper), "Outlier", "In Range")
    fig = px.box(
        plot_df,
        y=column,
        color="Outlier",
        points="all",
        template=template,
        title=f"IQR Outlier Detection: {column}",
        color_discrete_map={"Outlier": "#ef4444", "In Range": "#2563eb"},
    )
    fig.add_hline(y=lower, line_dash="dash", line_color="#f59e0b", annotation_text="Lower fence")
    fig.add_hline(y=upper, line_dash="dash", line_color="#f59e0b", annotation_text="Upper fence")
    fig.update_layout(height=500)
    return fig

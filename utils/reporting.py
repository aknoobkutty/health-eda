"""Downloadable report generation helpers."""

from __future__ import annotations

from io import BytesIO, StringIO
from textwrap import wrap

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

from utils.analysis import correlation_matrix, strong_correlations, summary_statistics
from utils.data_loader import dataset_overview


def build_insights(df: pd.DataFrame, numerical: list[str], categorical: list[str]) -> list[str]:
    """Generate plain-English dataset insights."""
    overview = dataset_overview(df)
    insights = [
        f"Dataset contains {overview['rows']:,} rows and {overview['columns']:,} columns.",
        f"Missing values account for {overview['missing_pct']}% of all cells.",
        f"Duplicate rows account for {overview['duplicate_pct']}% of the dataset.",
    ]
    if numerical:
        numeric_missing = df[numerical].isna().mean().sort_values(ascending=False)
        insights.append(f"Most incomplete numeric column: {numeric_missing.index[0]} ({numeric_missing.iloc[0] * 100:.2f}% missing).")
    if categorical:
        cat_cardinality = df[categorical].nunique(dropna=True).sort_values(ascending=False)
        insights.append(f"Highest-cardinality categorical column: {cat_cardinality.index[0]} ({int(cat_cardinality.iloc[0])} unique values).")

    corr = correlation_matrix(df, numerical)
    strong = strong_correlations(corr, threshold=0.7)
    if not strong.empty:
        top = strong.iloc[0]
        insights.append(
            f"Strongest observed correlation: {top['Feature 1']} vs {top['Feature 2']} "
            f"({top['Correlation']}, {top['Direction'].lower()})."
        )
    else:
        insights.append("No feature pairs exceeded the strong correlation threshold of 0.70.")
    return insights


def build_csv_summary(df: pd.DataFrame, numerical: list[str], categorical: list[str]) -> str:
    """Build a CSV-formatted summary export."""
    numeric_summary, categorical_summary = summary_statistics(df, numerical, categorical)
    buffer = StringIO()
    buffer.write("# Dataset Overview\n")
    pd.DataFrame([dataset_overview(df)]).to_csv(buffer, index=False)
    buffer.write("\n# Numeric Summary\n")
    numeric_summary.to_csv(buffer)
    buffer.write("\n# Categorical Summary\n")
    categorical_summary.to_csv(buffer, index=False)
    return buffer.getvalue()


def build_pdf_report(df: pd.DataFrame, numerical: list[str], categorical: list[str]) -> bytes:
    """Generate a compact PDF report using Matplotlib only."""
    insights = build_insights(df, numerical, categorical)
    overview = dataset_overview(df)
    numeric_summary, _ = summary_statistics(df, numerical, categorical)
    corr = correlation_matrix(df, numerical)

    buffer = BytesIO()
    with PdfPages(buffer) as pdf:
        fig = plt.figure(figsize=(11, 8.5))
        fig.suptitle("Automated EDA Report", fontsize=20, fontweight="bold")
        y = 0.86
        overview_lines = [
            f"Rows: {overview['rows']:,}",
            f"Columns: {overview['columns']:,}",
            f"Missing Cells: {overview['missing_cells']:,} ({overview['missing_pct']}%)",
            f"Duplicate Rows: {overview['duplicate_rows']:,} ({overview['duplicate_pct']}%)",
            f"Memory Usage: {overview['memory_mb']} MB",
        ]
        for line in overview_lines:
            fig.text(0.08, y, line, fontsize=12)
            y -= 0.045
        fig.text(0.08, y - 0.02, "Key Insights", fontsize=14, fontweight="bold")
        y -= 0.075
        for insight in insights:
            for wrapped in wrap(f"- {insight}", width=95):
                fig.text(0.08, y, wrapped, fontsize=11)
                y -= 0.04
        plt.axis("off")
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        if not numeric_summary.empty:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            ax.axis("off")
            ax.set_title("Numeric Summary Statistics", fontsize=16, fontweight="bold", pad=20)
            table_data = numeric_summary.head(12).round(3)
            table = ax.table(
                cellText=table_data.values,
                colLabels=table_data.columns,
                rowLabels=table_data.index,
                loc="center",
                cellLoc="center",
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.4)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

        if not corr.empty:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            heatmap = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
            ax.set_title("Correlation Matrix", fontsize=16, fontweight="bold", pad=20)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=8)
            ax.set_yticklabels(corr.columns, fontsize=8)
            fig.colorbar(heatmap, ax=ax, shrink=0.75)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    buffer.seek(0)
    return buffer.read()

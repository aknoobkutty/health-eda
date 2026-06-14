# Universal Streamlit EDA Dashboard

A production-ready Streamlit application for automated exploratory data analysis on any uploaded CSV dataset, including a MedInsight-style healthcare appointment no-show dashboard.

## Folder Structure

```text
.
|-- app.py
|-- requirements.txt
|-- README.md
|-- pages/
|   |-- __init__.py
|   |-- correlation.py
|   |-- data_quality.py
|   |-- eda.py
|   |-- healthcare_mode.py
|   |-- machine_learning.py
|   |-- outliers.py
|   |-- overview.py
|   |-- reports.py
|   |-- statistical_analysis.py
|   `-- transformation.py
`-- utils/
    |-- __init__.py
    |-- analysis.py
    |-- config.py
    |-- data_loader.py
    |-- healthcare.py
    |-- ml.py
    |-- reporting.py
    `-- visualization.py
```

## Quick Start

1. Create and activate a virtual environment.

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Run the app.

```bash
streamlit run app.py
```

4. Upload any CSV file from the sidebar.

## Features

- CSV upload with preview, dataset information, and automatic column type detection.
- Data quality checks for missing values, duplicates, data types, and null value visualization.
- Automated EDA with histograms, boxplots, violin plots, count plots, pie charts, and summary statistics.
- Correlation matrix, Plotly heatmap, and strong positive or negative relationship detection.
- Statistical analysis with Chi-Square test, ANOVA, skewness, kurtosis, and normality tests.
- IQR outlier detection with visual inspection.
- Log and Box-Cox transformations with transformed dataset download.
- Classification workflow with Logistic Regression, Decision Tree, and Random Forest.
- Metrics include accuracy, precision, recall, F1 score, and confusion matrix.
- Downloadable PDF report, CSV summary, and text insights.
- Light and dark dashboard themes with a polished healthcare analytics layout.
- MedInsight-inspired sidebar, KPI cards, chart panels, quick actions, and AI insight panel.

## Healthcare Mode

Healthcare Mode activates automatically for Medical Appointment No-Shows style datasets that include fields such as:

- `AppointmentDay`
- `ScheduledDay`
- `Age`
- `SMS_received`
- `No-show`

When detected, the dashboard adds:

- No-show rate analysis
- SMS effectiveness analysis
- Waiting time analysis
- Age group analysis
- Doctor allocation recommendations by neighbourhood

## Architecture

The app follows a modular structure:

- `app.py` handles startup, upload state, theme selection, and sidebar navigation.
- `pages/` contains Streamlit page renderers.
- `utils/` contains reusable logic for profiling, plotting, statistics, machine learning, healthcare analysis, and reporting.

This keeps the user interface separate from the analytical logic and makes the dashboard easier to test, maintain, and extend.

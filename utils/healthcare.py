"""Healthcare appointment no-show analysis helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd


NO_SHOW_COLUMNS = {
    "patientid",
    "appointmentid",
    "gender",
    "scheduledday",
    "appointmentday",
    "age",
    "neighbourhood",
    "sms_received",
    "no-show",
}


def _normalized_columns(df: pd.DataFrame) -> dict[str, str]:
    return {str(col).strip().lower().replace(" ", "_"): col for col in df.columns}


def detect_no_show_dataset(df: pd.DataFrame) -> bool:
    """Detect the common Medical Appointment No-Shows dataset schema."""
    normalized = set(_normalized_columns(df).keys())
    required = {"appointmentday", "scheduledday", "age", "sms_received", "no-show"}
    return required.issubset(normalized) or len(NO_SHOW_COLUMNS.intersection(normalized)) >= 6


def prepare_no_show_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize healthcare dataset fields used by the analysis."""
    mapping = _normalized_columns(df)
    data = df.copy()

    no_show_col = mapping.get("no-show") or mapping.get("no_show")
    appointment_col = mapping.get("appointmentday") or mapping.get("appointment_day")
    scheduled_col = mapping.get("scheduledday") or mapping.get("scheduled_day")
    sms_col = mapping.get("sms_received")
    age_col = mapping.get("age")

    if no_show_col:
        data["NoShowFlag"] = data[no_show_col].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0, "1": 1, "0": 0})
    if appointment_col and scheduled_col:
        data["AppointmentDate"] = pd.to_datetime(data[appointment_col], errors="coerce")
        data["ScheduledDate"] = pd.to_datetime(data[scheduled_col], errors="coerce")
        data["WaitingDays"] = (data["AppointmentDate"].dt.normalize() - data["ScheduledDate"].dt.normalize()).dt.days
        data.loc[data["WaitingDays"] < 0, "WaitingDays"] = np.nan
    if sms_col:
        data["SMSReceived"] = pd.to_numeric(data[sms_col], errors="coerce").fillna(0).astype(int)
    if age_col:
        data["AgeClean"] = pd.to_numeric(data[age_col], errors="coerce")
        bins = [-1, 12, 18, 35, 50, 65, 120]
        labels = ["Child", "Teen", "Young Adult", "Adult", "Older Adult", "Senior"]
        data["AgeGroup"] = pd.cut(data["AgeClean"], bins=bins, labels=labels)
    return data


def no_show_summary(df: pd.DataFrame) -> dict[str, object]:
    data = prepare_no_show_data(df)
    if "NoShowFlag" not in data:
        raise ValueError("No-show column could not be identified.")
    rate = data["NoShowFlag"].mean() * 100
    return {
        "appointments": int(len(data)),
        "no_show_rate": round(float(rate), 2),
        "show_rate": round(float(100 - rate), 2),
        "sms_rate": round(float(data["SMSReceived"].mean() * 100), 2) if "SMSReceived" in data else None,
        "avg_waiting_days": round(float(data["WaitingDays"].mean()), 2) if "WaitingDays" in data else None,
    }


def grouped_no_show_rate(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    data = prepare_no_show_data(df)
    if "NoShowFlag" not in data or group_col not in data:
        return pd.DataFrame()
    grouped = (
        data.dropna(subset=[group_col])
        .groupby(group_col, observed=False)["NoShowFlag"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "Appointments", "mean": "No-show Rate"})
    )
    grouped["No-show Rate"] = (grouped["No-show Rate"] * 100).round(2)
    return grouped.sort_values("No-show Rate", ascending=False)


def sms_effectiveness(df: pd.DataFrame) -> pd.DataFrame:
    return grouped_no_show_rate(df, "SMSReceived")


def waiting_time_analysis(df: pd.DataFrame) -> pd.DataFrame:
    data = prepare_no_show_data(df)
    if "WaitingDays" not in data or "NoShowFlag" not in data:
        return pd.DataFrame()
    bins = [-0.1, 0, 3, 7, 14, 30, 3650]
    labels = ["Same day", "1-3 days", "4-7 days", "8-14 days", "15-30 days", "30+ days"]
    data["Waiting Bucket"] = pd.cut(data["WaitingDays"], bins=bins, labels=labels)
    return grouped_no_show_rate(data, "Waiting Bucket")


def doctor_allocation_recommendations(df: pd.DataFrame) -> pd.DataFrame:
    """Create practical allocation recommendations from demand and no-show risk."""
    data = prepare_no_show_data(df)
    mapping = _normalized_columns(data)
    neighbourhood_col = mapping.get("neighbourhood")
    if not neighbourhood_col or "NoShowFlag" not in data:
        return pd.DataFrame()

    grouped = (
        data.groupby(neighbourhood_col)["NoShowFlag"]
        .agg(Appointments="count", NoShowRate="mean")
        .reset_index()
    )
    grouped["NoShowRate"] = (grouped["NoShowRate"] * 100).round(2)
    high_volume = grouped["Appointments"].quantile(0.75)
    high_no_show = grouped["NoShowRate"].quantile(0.75)

    def recommendation(row: pd.Series) -> str:
        if row["Appointments"] >= high_volume and row["NoShowRate"] >= high_no_show:
            return "Add reminder capacity and overbooking buffer"
        if row["Appointments"] >= high_volume:
            return "Prioritize doctor coverage for high appointment volume"
        if row["NoShowRate"] >= high_no_show:
            return "Target confirmations before assigning extra capacity"
        return "Maintain standard allocation"

    grouped["Recommendation"] = grouped.apply(recommendation, axis=1)
    return grouped.sort_values(["Appointments", "NoShowRate"], ascending=False)

"""Healthcare appointment no-show dashboard page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.config import kpi_card
from utils.healthcare import (
    detect_no_show_dataset,
    doctor_allocation_recommendations,
    grouped_no_show_rate,
    no_show_summary,
    prepare_no_show_data,
    sms_effectiveness,
    waiting_time_analysis,
)


def render(df: pd.DataFrame, template: str) -> None:
    """Render healthcare-specific analysis when the schema is detected."""
    st.subheader("Healthcare Mode")
    detected = detect_no_show_dataset(df)

    if not detected:
        st.info(
            "This mode activates automatically for Medical Appointment No-Shows style datasets "
            "with fields such as AppointmentDay, ScheduledDay, Age, SMS_received, and No-show."
        )
        return

    data = prepare_no_show_data(df)
    summary = no_show_summary(df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Appointments", f"{summary['appointments']:,}")
    with c2:
        kpi_card("No-show Rate", f"{summary['no_show_rate']}%")
    with c3:
        kpi_card("SMS Coverage", f"{summary['sms_rate']}%" if summary["sms_rate"] is not None else "N/A")
    with c4:
        kpi_card("Avg Waiting Days", f"{summary['avg_waiting_days']}" if summary["avg_waiting_days"] is not None else "N/A")

    tab_no_show, tab_sms, tab_waiting, tab_age, tab_doctors = st.tabs(
        [
            "No-show Analysis",
            "SMS Effectiveness",
            "Waiting Time",
            "Age Groups",
            "Doctor Allocation",
        ]
    )

    with tab_no_show:
        group_options = [col for col in ["Gender", "Neighbourhood", "Scholarship", "Hipertension", "Diabetes", "Alcoholism"] if col in data.columns]
        if group_options:
            group = st.selectbox("Analyze no-show rate by", group_options)
            grouped = grouped_no_show_rate(data, group)
            st.plotly_chart(
                px.bar(grouped.head(25), x=group, y="No-show Rate", color="Appointments", template=template, title=f"No-show Rate by {group}"),
                use_container_width=True,
            )
            st.dataframe(grouped, use_container_width=True, hide_index=True)
        else:
            st.info("No supported grouping columns were found.")

    with tab_sms:
        sms = sms_effectiveness(data)
        if sms.empty:
            st.info("SMS_received column was not found.")
        else:
            sms["SMSReceived"] = sms["SMSReceived"].map({0: "No SMS", 1: "SMS Received"}).fillna(sms["SMSReceived"])
            st.plotly_chart(px.bar(sms, x="SMSReceived", y="No-show Rate", text="No-show Rate", template=template), use_container_width=True)
            st.dataframe(sms, use_container_width=True, hide_index=True)

    with tab_waiting:
        waiting = waiting_time_analysis(data)
        if waiting.empty:
            st.info("Waiting time could not be calculated.")
        else:
            st.plotly_chart(
                px.line(waiting, x="Waiting Bucket", y="No-show Rate", markers=True, template=template, title="No-show Rate by Waiting Time"),
                use_container_width=True,
            )
            st.dataframe(waiting, use_container_width=True, hide_index=True)

    with tab_age:
        age = grouped_no_show_rate(data, "AgeGroup")
        if age.empty:
            st.info("Age group analysis could not be calculated.")
        else:
            st.plotly_chart(px.bar(age, x="AgeGroup", y="No-show Rate", color="Appointments", template=template), use_container_width=True)
            st.dataframe(age, use_container_width=True, hide_index=True)

    with tab_doctors:
        recommendations = doctor_allocation_recommendations(data)
        if recommendations.empty:
            st.info("Doctor allocation recommendations require a Neighbourhood column and no-show labels.")
        else:
            st.dataframe(recommendations, use_container_width=True, hide_index=True)

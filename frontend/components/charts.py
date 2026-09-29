import streamlit as st
import pandas as pd
import altair as alt
from typing import Dict, Any, List

def render_disease_distribution_chart(disease_distribution: List[Dict[str, Any]]):
    """Renders Altair Bar Chart of disease frequencies in biophilic green tones."""
    if not disease_distribution:
        st.info("No scan history data available for visualization.")
        return

    df = pd.DataFrame(disease_distribution)
    df.columns = ["Disease", "Count"]

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=8)
        .encode(
            x=alt.X("Count:Q", title="Number of Scans"),
            y=alt.Y("Disease:N", sort="-x", title="Disease Class"),
            color=alt.Color(
                "Disease:N",
                scale=alt.Scale(
                    domain=["Healthy", "Leaf Blight", "Leaf Spot", "Bud Rot", "Stem Bleeding", "Caterpillar", "Yellowing"],
                    range=["#2a9d8f", "#d90429", "#f77f00", "#9d0208", "#e76f51", "#b7094c", "#e9c46a"]
                ),
                legend=None
            ),
            tooltip=["Disease", "Count"]
        )
        .properties(height=280)
        .configure_axis(labelFontSize=12, titleFontSize=13, labelColor="#1f2923", titleColor="#1b4332")
        .configure_view(stroke=None)
    )

    st.altair_chart(chart, use_container_width=True)

def render_health_ratio_donut(healthy_scans: int, diseased_scans: int):
    """Renders Altair Donut Chart for Healthy vs Diseased palms."""
    if healthy_scans + diseased_scans == 0:
        st.info("No scans recorded yet.")
        return

    df = pd.DataFrame([
        {"Category": "Healthy Palms", "Scans": healthy_scans},
        {"Category": "Diseased Palms", "Scans": diseased_scans}
    ])

    chart = (
        alt.Chart(df)
        .mark_arc(innerRadius=65, stroke="#ffffff", strokeWidth=2)
        .encode(
            theta=alt.Theta(field="Scans", type="quantitative"),
            color=alt.Color(
                field="Category",
                type="nominal",
                scale=alt.Scale(domain=["Healthy Palms", "Diseased Palms"], range=["#2a9d8f", "#d90429"])
            ),
            tooltip=["Category", "Scans"]
        )
        .properties(height=280)
        .configure_view(stroke=None)
    )

    st.altair_chart(chart, use_container_width=True)

def render_expense_breakdown_chart(category_breakdown: Dict[str, float]):
    """Renders Altair Bar Chart of farm expenses by category in green tones."""
    items = [{"Category": cat, "Amount": amt} for cat, amt in category_breakdown.items() if amt > 0]
    if not items:
        st.info("No expense data recorded yet for chart visualization.")
        return

    df = pd.DataFrame(items)

    chart = (
        alt.Chart(df)
        .mark_bar(cornerRadiusEnd=6)
        .encode(
            x=alt.X("Amount:Q", title="Amount (₹)"),
            y=alt.Y("Category:N", sort="-x", title="Expense Category"),
            color=alt.value("#2a9d8f"),
            tooltip=["Category", alt.Tooltip("Amount:Q", format=",.2f")]
        )
        .properties(height=260)
        .configure_axis(labelFontSize=11, titleFontSize=12, labelColor="#1f2923", titleColor="#1b4332")
        .configure_view(stroke=None)
    )

    st.altair_chart(chart, use_container_width=True)


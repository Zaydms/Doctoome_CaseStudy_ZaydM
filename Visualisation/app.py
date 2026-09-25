import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="Doctoome Campaign Dashboard",
    layout="wide"
)

# Colors
NAVY = "#14232B"
TEAL = "#1BB3B0"
WHITE = "#FFFFFF"
GREY = "#5A6872"
LIGHT_GREY = "#E3EBEE"
ORANGE = "#F7B84B"
RED = "#FF6B6B"

# Paths
project_root = Path(__file__).resolve().parent.parent
analytics_path = project_root / "data" / "analytics"


@st.cache_data
def load_data():
    visitors = pd.read_parquet(
        analytics_path / "visitor_analytics.parquet"
    )

    sessions = pd.read_parquet(
        analytics_path / "session_analytics.parquet"
    )

    questions = pd.read_parquet(
        analytics_path / "question_analytics.parquet"
    )

    return visitors, sessions, questions


visitors, sessions, questions = load_data()

st.title("Doctoome — Diabetes Awareness Campaign")
st.caption("Campaign performance, questionnaire behaviour and audience insights")


##outcomes distribution-Donut
outcomes = (
    sessions["outcome_category"]
    .dropna()
    .value_counts()
    .reset_index()
)

outcomes.columns = ["outcome", "sessions"]

fig = px.pie(
    outcomes,
    names="outcome",
    values="sessions",
    hole=0.60
)

fig.update_layout(
    title="Outcome Distribution",
    legend_title=""
)

st.plotly_chart(fig, use_container_width=True)

##June-July visitor growth
monthly_visitors = (
    sessions.assign(
        month=sessions["session_started_at"].dt.to_period("M").astype(str)
    )
    .groupby("month")["visitor_id"]
    .nunique()
)

june = monthly_visitors.get("2026-06", 0)
july = monthly_visitors.get("2026-07", 0)

growth = ((july - june) / june * 100) if june else 0

col1, col2, col3 = st.columns(3)

col1.metric("June Visitors", f"{june:,}")
col2.metric("July Visitors", f"{july:,}")
col3.metric("Growth", f"{growth:.1f}%")

##campaign performance- Bubble chart
campaign = (
    sessions
    .dropna(subset=["campaign_name"])
    .groupby("campaign_name")
    .agg(
        sessions=("session_id", "nunique"),
        visitors=("visitor_id", "nunique"),
        started=("started", "sum"),
        completed=("completed", "sum")
    )
    .reset_index()
)

campaign["completion_rate"] = (
    campaign["completed"]
    / campaign["started"]
    * 100
)

fig = px.scatter(
    campaign,
    x="sessions",
    y="completion_rate",
    size="visitors",
    text="campaign_name",
    hover_data=["started", "completed", "visitors"],
    title="Campaign Performance"
)

fig.update_traces(
    textposition="top center",
    marker=dict(color=TEAL)
)

fig.update_layout(
    xaxis_title="Sessions",
    yaxis_title="Completion Rate (%)"
)

st.plotly_chart(fig, use_container_width=True)

#questionnaire completuion


st.subheader("Question Answer Rate")

question_metrics = (
    questions
    .groupby("question_number", as_index=False)
    .agg(
        views=("session_id", "count"),
        answers=("answered", "sum")
    )
)

question_metrics["answer_rate"] = (
    question_metrics["answers"]
    / question_metrics["views"]
    * 100
)

question_metrics = question_metrics.sort_values("question_number")

question_metrics["question"] = (
    "Q" + question_metrics["question_number"].astype(str)
)

colors = [
    RED if q == 4 else TEAL
    for q in question_metrics["question_number"]
]

fig_questions = go.Figure()

fig_questions.add_trace(
    go.Bar(
        x=question_metrics["question"],  # PAS de [] autour
        y=question_metrics["answer_rate"],
        marker_color=colors,

        text=question_metrics["answer_rate"],
        texttemplate="%{text:.1f}%",
        textposition="outside",

        customdata=question_metrics[
            ["views", "answers"]
        ].to_numpy(),

        hovertemplate=(
            "<b>%{x}</b><br>"
            "Views: %{customdata[0]:,.0f}<br>"
            "Answers: %{customdata[1]:,.0f}<br>"
            "Answer rate: %{y:.2f}%"
            "<extra></extra>"
        )
    )
)

fig_questions.update_layout(
    xaxis_title="Question",
    yaxis_title="Answer Rate (%)",
    yaxis=dict(
        range=[0, 105],
        ticksuffix="%"
    ),
    showlegend=False
)

st.plotly_chart(
    fig_questions,
    use_container_width=True
)

##device x Acquisition source matrix
relevant_sources = [
    "google-organic",
    "google-ads",
    "chatgpt",
    "referral",
    "refferal",
    "email"
]

matrix = sessions[
    sessions["acquisition_source"].isin(relevant_sources)
].copy()

matrix = (
    matrix
    .groupby(["device_type", "acquisition_source"])
    .agg(
        sessions=("session_id", "count"),
        started=("started", "sum"),
        completed=("completed", "sum")
    )
    .reset_index()
)

matrix["completion_rate"] = (
    matrix["completed"]
    / matrix["started"]
    * 100
)

heatmap = matrix.pivot(
    index="device_type",
    columns="acquisition_source",
    values="completion_rate"
)

fig = px.imshow(
    heatmap,
    text_auto=".1f",
    aspect="auto",
    title="Completion Rate — Device × Acquisition Source"
)

st.plotly_chart(fig, use_container_width=True)

#risk patterns
st.subheader("Risk-related Answer Patterns")

risk_patterns = pd.DataFrame({
    "Pattern": [
        "Symptoms",
        "Symptoms",
        "Symptoms",

        "Family history",
        "Family history",
        "Family history",

        "Low physical activity",
        "Low physical activity",
        "Low physical activity"
    ],

    "Outcome": [
        "No current indication",
        "Declared diagnosed",
        "Possible risk",

        "No current indication",
        "Declared diagnosed",
        "Possible risk",

        "No current indication",
        "Declared diagnosed",
        "Possible risk"
    ],

    "Percentage": [
        10.14,
        24.43,
        53.25,

        15.23,
        32.26,
        62.16,

        13.19,
        29.81,
        57.91
    ]
})

fig_risk = px.bar(
    risk_patterns,
    x="Pattern",
    y="Percentage",
    color="Outcome",
    barmode="group",
    text="Percentage",
    color_discrete_map={
        "No current indication": TEAL,
        "Declared diagnosed": ORANGE,
        "Possible risk": RED
    }
)

fig_risk.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="outside"
)

fig_risk.update_layout(
    xaxis_title="",
    yaxis_title="Risk-associated answers (%)",
    yaxis_range=[0, 70],
    legend_title="Outcome"
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)
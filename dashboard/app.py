import json
import streamlit as st
from pathlib import Path
import pandas as pd
import altair as alt
from datetime import timedelta

# ----------------------
# Page Config
# ----------------------
st.set_page_config(
    page_title="Autonomous SRE Dashboard",
    layout="wide"
)

# ----------------------
# High-Contrast Professional CSS
# ----------------------
st.markdown("""
<style>
body {
    background-color: #0d1117;
    color: #ffffff;
}
.block-container {
    max-width: 1500px;
    padding-top: 1rem;
}
.card {
    background-color: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 14px;
}
.h1 {
    font-size: 22px;
    font-weight: 600;
}
.h2 {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 8px;
}
.text-secondary {
    color: #e6edf3;
    font-size: 14px;
}
.text-muted {
    color: #9da7b3;
    font-size: 12px;
}
.metric {
    font-size: 28px;
    font-weight: 600;
}
.sev-high {
    color: #ff7b72;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# Load Data
# ----------------------
latest_path = Path("dashboard/latest_incident.json")
index_path = Path("reports/index.json")

if not latest_path.exists() or not index_path.exists():
    st.error("Run workflow at least once to generate reports.")
    st.stop()

with open(latest_path) as f:
    latest = json.load(f)

with open(index_path) as f:
    index = json.load(f)

df = pd.DataFrame(index)
df["detected_at"] = pd.to_datetime(df["detected_at"])

incident = latest["incident"]
snapshot = incident["metrics_snapshot"]

# ----------------------
# HEADER
# ----------------------
st.markdown(f"""
<div class="card">
    <div class="h1">Incident {incident['incident_id']}</div>
    <div class="text-secondary">
        Service: <b>{incident['service']}</b> |
        Severity: <span class="sev-high">{incident['severity']}</span> |
        Detected: {incident['detected_at']}
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------------
# SERVICE HEALTH (CARDS)
# ----------------------
st.markdown('<div class="h2">Service Health</div>', unsafe_allow_html=True)

cpu = snapshot["compute"]["cpu_percent"]["value"]
error_rate = snapshot["traffic"]["error_rate_percent"]["value"]
lat_p95 = snapshot["latency"]["latency_ms_p95"]["value"]

c1, c2, c3 = st.columns(3)

c1.markdown(f"""
<div class="card">
    <div class="text-muted">CPU Usage</div>
    <div class="metric">{cpu}%</div>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="card">
    <div class="text-muted">Error Rate</div>
    <div class="metric">{error_rate}%</div>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="card">
    <div class="text-muted">Latency (p95)</div>
    <div class="metric">{lat_p95} ms</div>
</div>
""", unsafe_allow_html=True)

# ----------------------
# SERVICE HEALTH BAR CHART
# ----------------------
health_df = pd.DataFrame({
    "Metric": ["CPU %", "Error Rate %", "Latency p95 (ms)"],
    "Value": [cpu, error_rate, lat_p95]
})

health_bar = (
    alt.Chart(health_df)
    .mark_bar(color="#58a6ff")
    .encode(
        x=alt.X("Metric:N", title=""),
        y=alt.Y("Value:Q", title="Value"),
        tooltip=["Metric", "Value"]
    )
    .properties(height=250)
)

st.altair_chart(health_bar, width="stretch")

# ----------------------
# ROOT CAUSE
# ----------------------
st.markdown('<div class="h2">Root Cause</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="card text-secondary">
{latest['root_cause']}
</div>
""", unsafe_allow_html=True)

# ============================================================
# INCIDENT HISTORY WITH FILTERS
# ============================================================
st.markdown('<div class="h2">Incident History</div>', unsafe_allow_html=True)

f1, f2, f3 = st.columns(3)

with f1:
    search_id = st.text_input("Search Incident ID")

with f2:
    period = st.selectbox("Date Filter", ["All", "Today", "This Week", "This Month"])

with f3:
    severity_filter = st.multiselect(
        "Severity",
        options=df["severity"].unique().tolist(),
        default=df["severity"].unique().tolist()
    )

filtered = df.copy()

if search_id:
    filtered = filtered[filtered["incident_id"].str.contains(search_id, case=False)]

filtered = filtered[filtered["severity"].isin(severity_filter)]

now = pd.Timestamp.utcnow()

if period == "Today":
    filtered = filtered[filtered["detected_at"].dt.date == now.date()]
elif period == "This Week":
    filtered = filtered[filtered["detected_at"] >= now - timedelta(days=7)]
elif period == "This Month":
    filtered = filtered[filtered["detected_at"] >= now - timedelta(days=30)]

# ----------------------
# INCIDENT VOLUME BAR CHART
# ----------------------
st.markdown('<div class="h2">Incident Volume</div>', unsafe_allow_html=True)

if not filtered.empty:
    volume_df = filtered.copy()
    volume_df["date"] = volume_df["detected_at"].dt.date
    count_df = volume_df.groupby("date").size().reset_index(name="count")

    volume_bar = (
        alt.Chart(count_df)
        .mark_bar(color="#7ee787")
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("count:Q", title="Incident Count"),
            tooltip=["date", "count"]
        )
        .properties(height=300)
    )

    st.altair_chart(volume_bar, width="stretch")
else:
    st.info("No incidents to display for selected filters.")

# ----------------------
# SEVERITY PIE CHART
# ----------------------
st.markdown('<div class="h2">Severity Distribution</div>', unsafe_allow_html=True)

if not filtered.empty:
    sev_df = filtered.groupby("severity").size().reset_index(name="count")

    severity_pie = (
        alt.Chart(sev_df)
        .mark_arc(innerRadius=60)
        .encode(
            theta="count:Q",
            color=alt.Color(
                "severity:N",
                scale=alt.Scale(
                    domain=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    range=["#da3633", "#ff7b72", "#d29922", "#3fb950"]
                )
            ),
            tooltip=["severity", "count"]
        )
        .properties(height=300)
    )

    st.altair_chart(severity_pie, width="stretch")
else:
    st.info("No severity data available.")

# ----------------------
# INCIDENT TABLE
# ----------------------
st.markdown('<div class="h2">Incident Table</div>', unsafe_allow_html=True)

if filtered.empty:
    st.info("No incidents match the selected filters.")
    st.stop()

st.dataframe(
    filtered.sort_values("detected_at", ascending=False)[
        ["incident_id", "service", "severity", "detected_at"]
    ],
    width="stretch",
    hide_index=True
)

# ----------------------
# REPORT DOWNLOAD (SAFE)
# ----------------------
st.markdown('<div class="h2">Download Report</div>', unsafe_allow_html=True)

selected = st.selectbox(
    "Select Incident",
    filtered["incident_id"].tolist()
)

selected_rows = filtered[filtered["incident_id"] == selected]

if selected_rows.empty:
    st.warning("No report available for the selected incident.")
    st.stop()

row = selected_rows.iloc[0]

with open(row["pdf_path"], "rb") as f:
    st.download_button(
        "Download PDF",
        data=f,
        file_name=Path(row["pdf_path"]).name,
        mime="application/pdf"
    )

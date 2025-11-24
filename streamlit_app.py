import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

st.set_page_config(page_title="SPL Monitor", page_icon="🔊")

# -------------------------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------------------------

@st.cache_data
def load_spl_data():
    """Fetch SPL time-series data from MongoDB and return as a DataFrame."""
    url = "mongodb+srv://petr:password@cluster0.bysfd7d.mongodb.net/?appName=Cluster0"
    client = MongoClient(url)

    db = client["Petr"]
    collection = db["SPL_data"]

    docs = list(collection.find({}, {"_id": 0}))  # don't include _id

    if not docs:
        return pd.DataFrame(columns=["timestamp", "Value"])

    df = pd.DataFrame(docs)

    # Convert timestamp strings → real datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Remove broken entries
    df = df.dropna(subset=["timestamp"])

    return df.sort_values("timestamp")


# -------------------------------------------------------------------
# LOAD DATA
# -------------------------------------------------------------------

df = load_spl_data()

st.title("🔊 SPL A-Weighted Monitor")

if df.empty:
    st.warning("No SPL data found in MongoDB.")
    st.stop()

# -------------------------------------------------------------------
# FILTERS
# -------------------------------------------------------------------

min_time = df["timestamp"].min()
max_time = df["timestamp"].max()

st.subheader("Filter Time Range")

start, end = st.slider(
    "Select time window:",
    min_value=min_time.to_pydatetime(),
    max_value=max_time.to_pydatetime(),
    value=(min_time.to_pydatetime(), max_time.to_pydatetime())
)

filtered = df[(df["timestamp"] >= start) & (df["timestamp"] <= end)]

# -------------------------------------------------------------------
# CHART
# -------------------------------------------------------------------

st.subheader("A-Weighted Sound Pressure Level Over Time")

st.line_chart(
    filtered,
    x="timestamp",
    y="Value"
)

# -------------------------------------------------------------------
# STATS
# -------------------------------------------------------------------

st.subheader("Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Min dB(A)", f"{filtered['Value'].min():.1f}")

with col2:
    st.metric("Max dB(A)", f"{filtered['Value'].max():.1f}")

with col3:
    st.metric("Avg dB(A)", f"{filtered['Value'].mean():.1f}")

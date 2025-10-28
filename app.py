import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
from vega_datasets import data
import json, urllib.request
import time

st.title("Week 10 Assignment - Animation")
st.header(
    "This weeks assignment is take any of your previous submissions and add an animation that is focused on a specific insight.",
    divider="gray"
)

# ---- Load earthquakes (vega_datasets) and normalize ----
json_url = data.earthquakes.url
with urllib.request.urlopen(json_url) as f:
    raw = json.load(f)

df = pd.json_normalize(raw["features"])

# Extract lon/lat from geometry
df["Long"] = pd.to_numeric(df["geometry.coordinates"].apply(lambda x: x[0]), errors="coerce")
df["Lat"]  = pd.to_numeric(df["geometry.coordinates"].apply(lambda x: x[1]), errors="coerce")

# Parse time (ms since epoch)
df["date_str"] = pd.to_datetime(df["properties.time"], unit="ms")
df["magnitude"] = pd.to_numeric(df["properties.mag"], errors="coerce")

# Keep valid rows only
df = df.dropna(subset=["Lat", "Long", "magnitude"]).reset_index(drop=True)

TOTAL = len(df)
min_mag = float(df["magnitude"].min())
max_mag = float(df["magnitude"].max())

# -------------------------
# Session state
# -------------------------
if "playing" not in st.session_state:
    st.session_state.playing = False
if "reveal" not in st.session_state:
    st.session_state.reveal = 1          # how many rows are currently revealed

# -------------------------
# Controls
# -------------------------
with st.sidebar:
    st.markdown("### Animation Controls")
    c1, c2, c3 = st.columns([1,1,1])
    if c1.button("▶ Play"):
        st.session_state.playing = True
    if c2.button("⏸ Pause"):
        st.session_state.playing = False
    if c3.button("⟲ Reset"):
        st.session_state.reveal = 1
        st.session_state.playing = False

    batch_size = st.slider("Points per tick", min_value=10, max_value=200, value=100, step=10)
    loop = st.toggle("Loop when finished", value=True)

# st.write("Currently Playing:", st.session_state.playing)
# st.write(f"Visible rows: {st.session_state.reveal} / {TOTAL}")
# st.write(f"Min Mag: {min_mag} — Max Mag: {max_mag}")

# -------------------------
# Chart builder
# -------------------------
countries = alt.topo_feature(data.world_110m.url, "countries")

def build_chart(df_visible: pd.DataFrame) -> alt.Chart:
    base = (
        alt.Chart(countries)
        .mark_geoshape(fill="lightgray", stroke="white")
        .properties(width=900, height=480)
    )

    points = (
        alt.Chart(df_visible)
        .mark_circle(opacity=0.95, stroke="black", strokeWidth=0.3)
        .encode(
            longitude="Long:Q",
            latitude="Lat:Q",
            color=alt.Color(
                "magnitude:Q",
                scale=alt.Scale(scheme="inferno", domain=[min_mag, max_mag], clamp=True),
                legend=alt.Legend(title="Magnitude"),
            ),
            size=alt.Size("magnitude:Q", scale=alt.Scale(range=[40, 700]), legend=None),
            tooltip=[
                "properties.place:N",
                "magnitude:Q",
                "date_str:T",
                "properties.type:N",
            ],
        )
    )

    return alt.layer(base, points).project(type="naturalEarth1").properties(
        title="Earthquakes (revealed progressively)"
    )

# Single placeholder we will update each tick
chart_ph = st.empty()

# Render current state once
current = df.iloc[: st.session_state.reveal]
chart_ph.altair_chart(build_chart(current), use_container_width=True)

# -------------------------
# Single-placeholder live animation (no reruns)
# -------------------------
chart_ph = st.empty()  # one spot to update the map

def render_chart(upto: int):
    """Render earthquakes up to a given index."""
    current = df.iloc[:upto]
    countries = alt.topo_feature(data.world_110m.url, "countries")

    base = (
        alt.Chart(countries)
        .mark_geoshape(fill="lightgray", stroke="white")
        .project(type="naturalEarth1")
        .properties(width=900, height=480)
    )

    points = (
        alt.Chart(current)
        .mark_circle(opacity=0.95, stroke="black", strokeWidth=0.3)
        .encode(
            longitude="Long:Q",
            latitude="Lat:Q",
            color=alt.Color(
                "magnitude:Q",
                scale=alt.Scale(scheme="inferno", domain=[min_mag, max_mag], clamp=True),
                legend=alt.Legend(title="Magnitude"),
            ),
            size=alt.Size("magnitude:Q", scale=alt.Scale(range=[40, 700]), legend=None),
            tooltip=[
                "properties.place:N",
                "magnitude:Q",
                "date_str:T",
                "properties.type:N",
            ],
        )
    )

    chart_ph.altair_chart(alt.layer(base, points), use_container_width=True)

# Initial render
reveal = getattr(st.session_state, "reveal", 1)
render_chart(reveal)

# Live animation loop (no reruns; you can scroll freely)
if st.session_state.playing:
    batch_size = 100  # or your slider value if you add one
    delay = 0.4       # seconds between frames

    i = reveal
    while i < len(df) and st.session_state.playing:
        i = min(i + batch_size, len(df))
        st.session_state.reveal = i
        render_chart(i)
        time.sleep(delay)

    # optionally loop or stop when done
    if i >= len(df):
        st.session_state.playing = False
import streamlit as st
import altair as alt
import pandas as pd
from numpy.random import default_rng as rng
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
long_, lat_ = [], []
for coords in df["geometry.coordinates"]:
    long_.append(coords[0])
    lat_.append(coords[1])
df["Lat"] = lat_
df["Long"] = long_
# properties.time is ms since epoch → parse correctly
df["date_str"] = pd.to_datetime(df["properties.time"], unit="ms")

# Build a reveal step for each row
MAX_STEP = len(df)  # total rows
df["step"] = np.arange(1, MAX_STEP + 1)

# -------------------------
# Session state
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1           # current reveal boundary (1..MAX_STEP)
if "playing" not in st.session_state:
    st.session_state.playing = False
if "loop" not in st.session_state:
    st.session_state.loop = True

# -------------------------
# Controls
# -------------------------
with st.sidebar:
    st.markdown("### Animation Controls")
    colA, colB, colC = st.columns([1, 1, 1])
    if colA.button("▶ Play"):
        st.session_state.playing = True
    if colB.button("⏸ Pause"):
        st.session_state.playing = False
    if colC.button("⟲ Reset"):
        st.session_state.step = 1
        st.session_state.playing = False

    # This slider sets how many points get added per tick
    batch_size = st.slider("Points per tick", 10, 100, 20, 10)

    # Loop when we reach the end?
    st.session_state.loop = st.toggle("Loop when finished", value=True)

st.write("Currently Playing:", st.session_state.playing)
st.write("Current Batch Size:", batch_size)
st.write("Min Mag:", df["properties.mag"].min())
st.write("Max Mag:", df["properties.mag"].max())


# -------------------------
# Map layers
# -------------------------
countries = alt.topo_feature(data.world_110m.url, "countries")

base = (
    alt.Chart(countries)
    .mark_geoshape(fill="lightgray", stroke="white")
    .project(type="naturalEarth1")
    .properties(width=900, height=480)
)

# Reveal only up to the current step
visible = df[df["step"] <= st.session_state.step]

points = (
    alt.Chart(visible)
    .mark_circle(size=160)
    .encode(
        longitude="Long:Q",
        latitude="Lat:Q",
        color=alt.Color(
            "properties.mag:Q",
            scale=alt.Scale(scheme="inferno", domain=[df["properties.mag"].min(), df["properties.mag"].max()]),
            legend=alt.Legend(title="Magnitude")),
        tooltip=["properties.mag:Q", "step:Q", "properties.type:N", "date_str:T"],
    )
)

# points = (
#     alt.Chart(visible)
#     .mark_circle()
#     .encode(
#         longitude="Long:Q",
#         latitude="Lat:Q",
#         color=alt.Color(
#             "properties.mag:Q",
#             scale=alt.Scale(scheme="inferno", domain=[df["properties.mag"].min(), df["properties.mag"].max()]),
#             legend=alt.Legend(title="Magnitude")
#         ),
#         size=alt.Size(
#             "properties.mag:Q",
#             scale=alt.Scale(range=[10, 400]),  # bigger points for larger magnitude
#             legend=None
#         ),
#         tooltip=[
#             "properties.place:N",
#             "properties.mag:Q",
#             "date_str:T",
#             "properties.type:N"
#         ],
#     )
# )


chart = (base + points).properties(title="Adding Points Over Time (Play/Pause/Reset)")
st.altair_chart(chart, use_container_width=True)

# -------------------------
# Animation loop: add `batch_size` points each tick while playing
# -------------------------
def advance_steps(batch: int):
    st.session_state.step = min(st.session_state.step + int(batch), MAX_STEP)
    if st.session_state.step >= MAX_STEP:
        if st.session_state.loop:
            st.session_state.step = 1
        else:
            st.session_state.playing = False

if st.session_state.playing:
    time.sleep(0.5)  # adjust tick speed
    advance_steps(batch_size)
    # Use modern API; fall back if running on older Streamlit
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

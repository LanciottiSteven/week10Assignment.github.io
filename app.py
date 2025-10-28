import streamlit as st
import altair as alt
import pandas as pd
from numpy.random import default_rng as rng
import numpy as np
from vega_datasets import data
import json, urllib.request
import time

st.title("Week 10 Assignment - Animation")

st.header("This weeks assignment is take any of your previous submissions and add an animation that is focused on a specific insight.", divider="gray")



# df = pd.DataFrame(rng(0).standard_normal((20, 3)), columns=["a", "b", "c"])

# point_selector = alt.selection_point("point_selection")
# interval_selector = alt.selection_interval("interval_selection")
# chart = (
#     alt.Chart(df)
#     .mark_circle()
#     .encode(
#         x="a",
#         y="b",
#         size="c",
#         color="c",
#         tooltip=["a", "b", "c"],
#         fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3)),
#     )
#     .add_params(point_selector, interval_selector)
# )

# event = st.altair_chart(chart, key="alt_chart", on_select="rerun")

# event

json_url = data.earthquakes.url
with urllib.request.urlopen(json_url) as f:
    raw = json.load(f)
    
df = pd.json_normalize(raw['features'])
long_ = []
lat_ = []
for i in df['geometry.coordinates']:
    long_.append(i[0])
    lat_.append(i[1])
df['Lat'] = lat_
df["Long"] = long_
df["date_str"] = pd.to_datetime(df["properties.time"])


MAX_STEP = int(len(df)+1)
df['step'] = np.arange(1,MAX_STEP)

# Session state
# -------------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "playing" not in st.session_state:
    st.session_state.playing = False
if "loop" not in st.session_state:
    st.session_state.loop = True




with st.sidebar:
    st.markdown("### Animation Controls")
    colA, colB, colC = st.columns([1,1,1])
    if colA.button("▶ Play"):
        st.session_state.playing = True
    if colB.button("⏸ Pause"):
        st.session_state.playing = False
    if colC.button("⟲ Reset"):
        st.session_state.step = 1
        st.session_state.playing = False

    speed = st.slider("Speed (points per second)", 0.25, 5.0, 1.0, 0.25)
    st.session_state.loop = st.toggle("Loop when finished", value=True)

st.write("[st.session_state.playing]")

countries = alt.topo_feature(data.world_110m.url, 'countries')
base = alt.Chart(countries).mark_geoshape(
    fill="lightgray",
    stroke="white"
).project(
    type="naturalEarth1"
).properties(
    width=900,
    height=480
).interactive()

visible = df[df["step"] <= st.session_state.step]

points = alt.Chart(visible).mark_circle(size=160).encode(
    longitude="Long:Q",
    latitude="Lat:Q",
    tooltip=["properties.mag:Q", "step:Q", "properties.type:N"]
)

chart = (base + points).properties(
    title="Adding Points Over Time (Play/Pause/Reset)"
)

st.altair_chart(chart, use_container_width=True)

# Animation loop (runs one tick, then re-runs the script)
# -------------------------
# def advance_one_step():
#     if st.session_state.step < MAX_STEP:
#         st.session_state.step += 1
#     else:
#         if st.session_state.loop:
#             st.session_state.step = 1
#         else:
#             st.session_state.playing = False

# # If playing, wait according to speed, then move one step and rerun
# if st.session_state.playing:
#     # convert points per second -> seconds per frame
#     delay = 1.0 / float(speed)
#     time.sleep(delay)
#     advance_one_step()
#     st.experimental_rerun()

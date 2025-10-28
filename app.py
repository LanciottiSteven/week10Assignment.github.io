import streamlit as st
import altair as alt
import pandas as pd
from numpy.random import default_rng as rng

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
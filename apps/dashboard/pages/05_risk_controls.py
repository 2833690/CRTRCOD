import streamlit as st

st.title("Risk Controls")
st.success("Kill switch: ACTIVE")
st.progress(0.0)
st.metric("Consecutive Losses", 0)
st.metric("Slippage Monitor", "OK")
for label in ["Pause Trading", "Close All Positions", "EMERGENCY STOP"]:
    st.warning(f"Confirm before {label}")
    confirm = st.checkbox(f"Confirm {label}")
    if st.button(label, disabled=not confirm):
        st.write(f"Requested: {label}")

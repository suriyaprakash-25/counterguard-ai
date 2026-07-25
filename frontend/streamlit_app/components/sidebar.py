import streamlit as st
from frontend.streamlit_app.api.client import health

def render_sidebar():
    st.sidebar.markdown("---")
    st.sidebar.write("### System Status")
    is_online = health()
    if is_online:
        st.sidebar.success("🟢 Backend Online")
    else:
        st.sidebar.error("🔴 Backend Offline")

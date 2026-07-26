import streamlit as st

from frontend.streamlit_app.components.sidebar import render_sidebar

st.set_page_config(
    page_title="CounterGuard | Home",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Premium Design
st.markdown(
    """
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stApp {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    }
    .hero {
        text-align: center;
        padding: 50px 20px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    h1 {
        font-size: 3rem !important;
        background: -webkit-linear-gradient(#eee, #333);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card {
        background: rgba(25, 30, 36, 0.7);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.05);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(0, 255, 170, 0.5);
    }
    .metric-title {
        font-size: 1.1rem;
        color: #8c8c8c;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00ffaa;
    }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
    <h1>🛡️ CounterGuard Dashboard</h1>
    <p style="font-size: 1.2rem; color: #ccc;">
        Autonomous Counterfeit & Grey-Market Intelligence Network
    </p>
</div>
<br>
""",
    unsafe_allow_html=True,
)

st.write("### 🌐 Live Global Telemetry")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """
    <div class="metric-card">
        <div class="metric-title">Active Investigations</div>
        <div class="metric-value">124</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
    <div class="metric-card">
        <div class="metric-title">Listings Scanned (24h)</div>
        <div class="metric-value">45.2K</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
    <div class="metric-card">
        <div class="metric-title">Counterfeits Detected</div>
        <div class="metric-value">89</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        """
    <div class="metric-card">
        <div class="metric-title">Enforcement Actions</div>
        <div class="metric-value">12</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.write("---")
st.write("### 🚨 Recent Alerts")
alerts_data = [
    {
        "ID": "INV-893",
        "Marketplace": "Amazon",
        "Status": "Investigating",
        "Confidence": "65%",
    },
    {
        "ID": "INV-892",
        "Marketplace": "eBay",
        "Status": "Action Required",
        "Confidence": "92%",
    },
    {
        "ID": "INV-891",
        "Marketplace": "AliExpress",
        "Status": "Monitoring",
        "Confidence": "40%",
    },
]
st.dataframe(alerts_data, use_container_width=True)

render_sidebar()

st.sidebar.success("Select a page above to drill down into investigations.")

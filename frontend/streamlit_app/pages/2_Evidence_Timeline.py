import streamlit as st

from frontend.streamlit_app.state import get_current_investigation

st.set_page_config(page_title="Evidence Timeline", page_icon="⏳")
st.title("⏳ Evidence Timeline")
st.write("Real-time collaborative querying between agents.")

st.markdown(
    """
<style>
    .timeline-item {
        padding: 15px;
        border-left: 3px solid #00ffaa;
        margin-bottom: 15px;
        background: rgba(255, 255, 255, 0.02);
        border-radius: 0 8px 8px 0;
    }
    .timeline-time {
        font-size: 0.8rem;
        color: #888;
    }
    .timeline-agent {
        font-weight: bold;
        color: #00ffaa;
    }
    .timeline-query {
        color: #ffa500;
        font-style: italic;
    }
</style>
""",
    unsafe_allow_html=True,
)

data = get_current_investigation()
if not data:
    st.warning(
        "No investigation data found. "
        "Please start an investigation on the Investigation page."
    )
else:
    for event in data.evidence_timeline:
        with st.expander(f"{event.timestamp} | {event.agent} ({event.action})"):
            action_class = (
                "timeline-query" if event.action in ["asks", "answers"] else ""
            )
            st.markdown(
                f"""
            <div class="timeline-item">
                <div class="timeline-time">{event.timestamp}</div>
                <div>
                    <span class="timeline-agent">{event.agent}</span>
                    <span style="color:#aaa;">[{event.action}]</span>
                </div>
                <div class="{action_class}">{event.detail}</div>
                <div style="font-size:0.9rem; margin-top:5px; color:#aaa;">
                    Confidence impact:
                    <span style="color:#00ffaa;">
                        +{event.confidence_delta}%
                    </span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

import streamlit as st

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

st.write("### Investigation INV-892 Log")

timeline_events = [
    {
        "time": "09:14:02",
        "agent": "Scout",
        "action": "discovered_listing",
        "detail": "Found new listing for 'Pro' Earbuds at $45.",
        "confidence_delta": "+10%",
    },
    {
        "time": "09:14:05",
        "agent": "Price Anomaly",
        "action": "flagged_price",
        "detail": "Price is 75% below retail baseline.",
        "confidence_delta": "+20%",
    },
    {
        "time": "09:14:10",
        "agent": "Seller Network Graph",
        "action": "asks",
        "detail": "→ Visual Agent: 'These three sellers appear related, compare logos across all three.'",
        "confidence_delta": "0%",
    },
    {
        "time": "09:14:15",
        "agent": "Visual Forensics",
        "action": "answers",
        "detail": "→ Seller Network Graph: 'Similarity score is 98%. Same batch defect detected.'",
        "confidence_delta": "+25%",
    },
    {
        "time": "09:14:20",
        "agent": "Mystery Shopper",
        "action": "asks",
        "detail": "→ Price Agent: 'If an invoice existed, would price still be suspicious?'",
        "confidence_delta": "0%",
    },
    {
        "time": "09:14:22",
        "agent": "Price Anomaly",
        "action": "answers",
        "detail": "→ Mystery Shopper: 'Yes, wholesale cost is minimum $80.'",
        "confidence_delta": "+15%",
    },
]

for event in timeline_events:
    action_class = "timeline-query" if event["action"] in ["asks", "answers"] else ""
    st.markdown(
        f"""
    <div class="timeline-item">
        <div class="timeline-time">{event["time"]}</div>
        <div><span class="timeline-agent">{event["agent"]}</span> <span style="color:#aaa;">[{event["action"]}]</span></div>
        <div class="{action_class}">{event["detail"]}</div>
        <div style="font-size:0.9rem; margin-top:5px; color:#aaa;">Confidence impact: <span style="color:#00ffaa;">{event["confidence_delta"]}</span></div>
    </div>
    """,
        unsafe_allow_html=True,
    )

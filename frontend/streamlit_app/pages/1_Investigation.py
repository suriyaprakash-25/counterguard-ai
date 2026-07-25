import pandas as pd
import streamlit as st

from frontend.streamlit_app.api.client import investigate

st.set_page_config(page_title="Investigation details", page_icon="🔍")

st.title("🔍 Active Investigation")

with st.form("investigation_form"):
    listing_url = st.text_input("Listing URL", value="https://ebay.com/itm/12345")
    marketplace = st.selectbox(
        "Marketplace", ["Amazon", "eBay", "AliExpress", "Walmart"]
    )
    submitted = st.form_submit_button("Start Investigation")

if submitted:
    with st.spinner("Investigating..."):
        data = investigate(listing_url, marketplace)
        if data:
            st.session_state.investigation_data = data
            st.success("Investigation complete!")
        else:
            st.error("Failed to fetch investigation data.")

if "investigation_data" in st.session_state:
    data = st.session_state.investigation_data

    st.markdown(
        """
    <style>
        .header-box {
            padding: 15px;
            border-radius: 8px;
            background-color: rgba(30, 40, 50, 0.8);
            border-left: 5px solid #00ffaa;
            margin-bottom: 20px;
        }
        .agent-status {
            padding: 10px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="header-box">
        <h4>Target: {data["listing_data"]["title"]}</h4>
        <p>Marketplace: {data["listing_data"]["marketplace"]} |
        Seller: {data["listing_data"]["seller"]}</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Confidence Score", f"{data['confidence_score']}%")
    col2.metric("Status", data["status"])
    col3.metric("Listing ID", data["listing_id"])

    st.subheader("Listing Details")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(
            "https://via.placeholder.com/300x200.png?text=Listing+Image",
            use_container_width=True,
        )
    with c2:
        st.write(f"**Listed Price:** {data['listing_data']['price']}")
        st.write(f"**Seller Location:** {data['listing_data']['location']}")
        st.write(f"**Quantity Sold:** {data['listing_data']['quantity_sold']}")
        st.write(f"**Listing Description:** '{data['listing_data']['description']}'")

    # Agent Status Panel
    st.subheader("Agent Status Panel")
    agents = ["Scout", "Visual", "Text", "Graph", "Price", "Mystery Shopper", "Fusion"]
    agent_status_html = '<div class="agent-status">'
    for agent in agents:
        agent_status_html += f"🟢 {agent} &nbsp;&nbsp; "
    agent_status_html += "⚪ Legal"
    agent_status_html += "</div>"
    st.markdown(agent_status_html, unsafe_allow_html=True)

    st.subheader("Agent Findings Summary")
    findings_list = []
    for agent, finding_data in data.get("agent_findings", {}).items():
        findings_list.append(
            {
                "Agent": agent,
                "Finding": finding_data["finding"],
                "Severity": finding_data["severity"],
            }
        )
    if findings_list:
        df = pd.DataFrame(findings_list)
        st.table(df)

    if data.get("legal_notice_draft"):
        st.subheader("Legal Draft")
        st.text_area("Draft Notice", data["legal_notice_draft"], height=200)

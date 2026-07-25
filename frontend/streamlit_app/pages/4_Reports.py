import streamlit as st

from frontend.streamlit_app.state import get_current_investigation

st.set_page_config(page_title="Reports & Escalation", page_icon="📑")

st.title("📑 Legal Escalation Reports")
st.write("Review auto-drafted takedown notices before human-in-the-loop approval.")

st.markdown(
    """
<style>
    .draft-box {
        background-color: #1e1e1e;
        border: 1px solid #333;
        border-radius: 8px;
        padding: 20px;
        font-family: monospace;
        color: #d4d4d4;
        white-space: pre-wrap;
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
    st.subheader(f"Pending Approval: {data.listing_id}")

    st.warning(
        "⚠️ **Human-in-the-Loop Required:** The Legal Agent "
        "has drafted this notice but cannot auto-file."
    )

    if data.legal_notice_draft:
        st.markdown(
            f'<div class="draft-box">{data.legal_notice_draft}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("No legal notice draft available for this investigation.")

    st.write("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "✅ Approve & File Notice", type="primary", use_container_width=True
        ):
            st.success("Notice approved and sent to marketplace API (Mocked).")
    with col2:
        if st.button("❌ Reject / Request Revision", use_container_width=True):
            st.error("Escalation rejected. Returning to queue.")

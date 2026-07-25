import streamlit as st

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

st.subheader("Pending Approval: INV-892")

st.warning(
    "⚠️ **Human-in-the-Loop Required:** The Legal Agent "
    "has drafted this notice but cannot auto-file."
    "⚠️ **Human-in-the-Loop Required:** The Legal Agent has drafted this notice but cannot auto-file."
)

draft_text = """[DRAFT TAKEDOWN NOTICE]
To: eBay Trust & Safety
Subject: Notice of Claimed Infringement - Counterfeit Goods

Dear eBay Legal Team,

I am writing on behalf of the intellectual property owner. We have a good faith
belief that the following listing(s) are offering counterfeit goods:

Listing ID: 9876543210
Seller ID: TechDeals_99
URL: https://ebay.com/itm/9876543210

Evidence Summary:
1. Product price is 75% below wholesale minimum (Anomaly Score: 0.95)
2. Image forensics indicate packaging logo misalignment consistent with known
   counterfeit batch C-44.
3. Seller network analysis links this account to 3 previously suspended sellers.
4. Seller failed to provide proof of authenticity when queried by mystery
   shopper.

Overall Confidence Score: 92%

We request the immediate removal of this listing.

Sincerely,
CounterGuard Legal AI (Pending Human Signature)
"""

st.markdown(f'<div class="draft-box">{draft_text}</div>', unsafe_allow_html=True)
st.write("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Approve & File Notice", type="primary", use_container_width=True):
        st.success("Notice approved and sent to marketplace API (Mocked).")
with col2:
    if st.button("❌ Reject / Request Revision", use_container_width=True):
        st.error("Escalation rejected. Returning to queue.")

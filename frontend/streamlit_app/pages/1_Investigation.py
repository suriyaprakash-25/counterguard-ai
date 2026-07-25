import streamlit as st
import pandas as pd

st.set_page_config(page_title="Investigation details", page_icon="🔍")

st.markdown("""
<style>
    .header-box {
        padding: 15px;
        border-radius: 8px;
        background-color: rgba(30, 40, 50, 0.8);
        border-left: 5px solid #00ffaa;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔍 Active Investigation: INV-892")

st.markdown("""
<div class="header-box">
    <h4>Target: Suspicious 'Pro' Model Earbuds</h4>
    <p>Marketplace: eBay | Seller: TechDeals_99</p>
</div>
""", unsafe_allow_html=True)

st.subheader("Listing Details")
col1, col2 = st.columns([1, 2])
with col1:
    st.image("https://via.placeholder.com/300x200.png?text=Listing+Image", use_container_width=True)
with col2:
    st.write("**Listed Price:** $45.00 (75% below retail)")
    st.write("**Seller Location:** Shenzhen, China")
    st.write("**Quantity Sold:** 430")
    st.write("**Listing Description:** '100% Genuine Pro Earbuds with noise cancelling. No box.'")

st.subheader("Agent Findings Summary")
findings = {
    "Agent": ["Visual Forensics", "Text Consistency", "Price Anomaly", "Seller Graph"],
    "Finding": ["Logo placement off by 2mm", "Description missing canonical SN", "Price is 4 standard deviations below mean", "Seller linked to 3 known suspended accounts"],
    "Severity": ["High", "Medium", "High", "Critical"]
}
df = pd.DataFrame(findings)
st.table(df)

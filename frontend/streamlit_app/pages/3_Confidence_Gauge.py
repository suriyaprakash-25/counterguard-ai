import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Confidence Gauge", page_icon="📈")

st.title("📈 Confidence Gauge")
st.write("Live confidence score aggregated from the Evidence Timeline.")

st.markdown("""
<style>
    .gauge-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
        background: rgba(0,0,0,0.2);
        border-radius: 15px;
        border: 1px solid rgba(255,255,255,0.05);
    }
</style>
""", unsafe_allow_html=True)

if "investigation_data" not in st.session_state:
    st.warning("No investigation data found. Please start an investigation on the Investigation page.")
else:
    data = st.session_state.investigation_data
    st.write(f"### Target: {data.get('listing_id', 'Unknown')}")

    # Gauge Chart using Plotly
    current_confidence = data.get('confidence_score', 0)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = current_confidence,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Counterfeit Probability", 'font': {'size': 24, 'color': 'white'}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "#00ffaa"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 40], 'color': 'green'},
                {'range': [40, 70], 'color': 'yellow'},
                {'range': [70, 100], 'color': 'red'}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70}
        },
        number={'font': {'color': 'white'}}
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Arial"}
    )

    st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.info(f"💡 **Routing Logic:** Confidence ≥ 70 routes to Legal Escalation Agent. Current score of {current_confidence}% triggers drafting of a takedown notice.")

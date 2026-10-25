
import os
import streamlit as st

from fundamental_analysis_agent.agents.orchestrator import OrchestratorAgent

st.set_page_config(
    page_title="Fundamental Analysis Agent",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Fundamental Analysis Agent")
st.caption("AI-assisted financial analysis, valuation, risk, and news sentiment.")

if not os.getenv("OPENAI_API_KEY"):
    st.error("OPENAI_API_KEY is not configured.")
    st.stop()

ticker = st.text_input(
    "Stock ticker",
    value="AAPL",
    max_chars=20,
).strip().upper()

if st.button("Analyze", type="primary"):
    if not ticker or not ticker.replace(".", "").replace("-", "").isalnum():
        st.error("Enter a valid ticker symbol.")
        st.stop()

    try:
        with st.spinner(f"Analyzing {ticker}..."):
            result = OrchestratorAgent().run(ticker)

        st.success(f"Analysis completed for {ticker}")

        for key, title in [
            ("final_report", "Final Report"),
            ("financial_report", "Financial Analysis"),
            ("news_report", "News & Sentiment"),
            ("risk_report", "Risk Analysis"),
            ("valuation_report", "Valuation"),
        ]:
            st.subheader(title)
            value = result.get(key, "Cannot be confirmed from available information.")
            if isinstance(value, (dict, list)):
                st.json(value)
            else:
                st.markdown(str(value))

    except Exception:
        st.error(
            "Analysis failed. Check the application logs for details. "
            "Do not expose API keys or other secrets in error messages."
        )
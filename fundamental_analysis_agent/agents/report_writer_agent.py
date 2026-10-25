import json
from ..llm_client import ask_llm

class ReportWriterAgent:
    """No data tools: synthesis only."""
    name = "ReportWriterAgent"

    def run(self, ticker, financial, news, risk, valuation):
        # Send compact specialist summaries, not raw statements or duplicate provider data.
        inputs = {
            "financial_summary": financial.get("analysis"),
            "key_ratios": financial.get("key_ratios"),
            "news_summary": news.get("analysis"),
            "risk_summary": risk.get("analysis"),
            "valuation_summary": valuation.get("analysis"),
            "dcf_scenario": valuation.get("dcf_scenario"),
        }
        return ask_llm(
            "Write a concise Markdown fundamental-analysis brief with investment verdict, "
            "financial health, valuation, risk, news sentiment, bull/base/bear considerations, "
            "data limitations and conclusion. Rating: STRONG BUY, BUY, HOLD, SELL, STRONG SELL, "
            "or INSUFFICIENT DATA. Explain evidence; don't mechanically convert sentiment into a "
            "rating. Label DCF as an assumption-driven scenario. Never invent facts. Educational "
            "research only, not personalized financial advice.",
            f"Ticker: {ticker}\nSpecialist summaries:\n{json.dumps(inputs, separators=(',', ':'), default=str)}"
        )

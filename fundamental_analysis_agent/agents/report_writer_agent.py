import json
from ..llm_client import ask_llm

class ReportWriterAgent:
    """No data tools: synthesis only."""
    name = "ReportWriterAgent"

    def run(self, ticker, financial, news, risk, valuation):
        inputs = {
            "financial_report": financial,
            "news_report": news,
            "risk_report": risk,
            "valuation_report": valuation,
        }
        return ask_llm(
            "Write a Markdown fundamental-analysis brief with investment verdict, financial "
            "health, valuation, risk, news sentiment, bull/base/bear considerations, data gaps, "
            "and conclusion. Rating must be STRONG BUY, BUY, HOLD, SELL, STRONG SELL, or "
            "INSUFFICIENT DATA. Explain the evidence and do not mechanically convert sentiment "
            "to a rating. Label DCF as an assumption-driven scenario. Never invent facts. "
            "Educational research only, not personalized financial advice.",
            f"Ticker: {ticker}\nFour specialist reports:\n{json.dumps(inputs, indent=2, default=str)}"
        )

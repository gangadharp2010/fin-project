import json
from ..tools import financial_tools as ft
from ..tools.news_tools import search_recent_news
from ..llm_client import ask_llm

class RiskAgent:
    name = "RiskAgent"

    def run(self, ticker):
        balance = ft.get_balance_sheet(ticker)
        ratios = ft.compute_key_ratios(ticker)
        headlines = list(search_recent_news(ticker))
        analysis = ask_llm(
            "Act as a sceptical risk manager. Assess leverage, liquidity, cash-flow quality, "
            "beta and headline risks only when supported. Assign LOW/MODERATE/ELEVATED/HIGH "
            "only if justified; otherwise state UNCONFIRMED. Do not invent stress-test results.",
            f"Ticker: {ticker}\nBalance sheet: {json.dumps(balance, default=str)}\n"
            f"Ratios: {json.dumps(ratios, default=str)}\nHeadlines: {json.dumps(headlines, default=str)}"
        )
        return {"agent": self.name, "balance_sheet": balance, "key_ratios": ratios,
                "news_used": headlines, "analysis": analysis}

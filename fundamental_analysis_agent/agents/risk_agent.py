from ..llm_client import ask_llm
from ..tools.financial_tools import compact_statement_context

class RiskAgent:
    name = "RiskAgent"

    def run(self, snapshot: dict) -> dict:
        compact = compact_statement_context(snapshot)
        # Only the selected balance-sheet rows, ratios, and a few headlines are passed.
        balance = compact.get("selected_statement_rows", {}).get("balance_sheet", {})
        ratios = compact.get("key_ratios", {})
        headlines = [{"title": h.get("title")} for h in compact.get("recent_headlines", [])[:5]]
        import json
        analysis = ask_llm(
            "Act as a sceptical risk manager. Assess leverage, liquidity, cash-flow quality, "
            "beta and headline risks only when evidence supports them. Assign LOW/MODERATE/"
            "ELEVATED/HIGH only when justified; otherwise UNCONFIRMED. Do not invent stress tests.",
            f"Ticker: {snapshot['ticker']}\nRatios: {json.dumps(ratios)}\n"
            f"Selected balance-sheet rows: {json.dumps(balance)}\nHeadlines: {json.dumps(headlines)}"
        )
        return {"agent": self.name, "analysis": analysis}

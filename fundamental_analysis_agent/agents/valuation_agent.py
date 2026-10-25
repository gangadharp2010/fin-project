import json
from ..tools import valuation_tools as vt
from ..llm_client import ask_llm

class ValuationAgent:
    name = "ValuationAgent"

    def run(self, ticker, financial_report):
        ratios = financial_report.get("key_ratios", {})
        dcf = vt.run_dcf_model(
            fcf=ratios.get("free_cash_flow"),
            current_price=ratios.get("current_price"),
            market_cap=ratios.get("market_cap"),
            total_debt=ratios.get("total_debt") or 0,
            cash=ratios.get("cash_and_equivalents") or 0,
        )
        peers = vt.get_peer_multiples(ticker)
        analysis = ask_llm(
            "Act as a valuation specialist. Explain the DCF scenario and limitations. "
            "Compare multiples with the candidate peer set, noting peers may not be direct "
            "competitors. Never silently present assumptions as facts.",
            f"Ticker: {ticker}\nRatios: {json.dumps(ratios, default=str)}\n"
            f"DCF scenario: {json.dumps(dcf, default=str)}\nPeer multiples: {json.dumps(peers, default=str)}"
        )
        return {"agent": self.name, "dcf_scenario": dcf,
                "calculation_note": "Illustrative scenario, not a forecast." if dcf else
                "Cannot be confirmed from available information.",
                "peer_multiples": peers, "analysis": analysis}

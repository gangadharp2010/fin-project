
from ..tools.valuation_tools import run_dcf_model, get_peer_multiples


class ValuationAgent:
    """Estimate valuation using available financial data."""

    def run(self, ticker: str, financial_report: dict, snapshot: dict) -> dict:
        ratios = snapshot.get("key_ratios", {})

        # Try common field names in the snapshot.
        info = snapshot.get("company_info", {})
        if not isinstance(info, dict):
            info = {}

        current_price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or snapshot.get("current_price")
        )

        market_cap = (
            info.get("marketCap")
            or snapshot.get("market_cap")
        )

        # Pass the required arguments to the DCF function.
        dcf = run_dcf_model(
            ratios,
            current_price,
            market_cap,
        )

        peers = get_peer_multiples(ticker)

        return {
            "ticker": ticker,
            "dcf_valuation": dcf,
            "peer_multiples": peers,
        }
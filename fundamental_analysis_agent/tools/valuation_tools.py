"""DCF scenario calculator and peer-multiple retrieval."""
from functools import lru_cache
from .financial_tools import fetch_snapshot


@lru_cache(maxsize=64)
def get_peer_multiples(ticker: str) -> dict:
    info = fetch_snapshot(ticker)
    sector = (info.get("sector") or "").lower()
    groups = {
        "technology": ["MSFT", "GOOGL", "AAPL", "ORCL", "IBM"],
        "healthcare": ["JNJ", "MRK", "ABBV", "PFE", "LLY"],
        "financial services": ["JPM", "BAC", "GS", "MS", "WFC"],
        "consumer cyclical": ["AMZN", "HD", "MCD", "NKE", "TSLA"],
        "consumer defensive": ["WMT", "COST", "PG", "KO", "PEP"],
        "communication services": ["GOOGL", "META", "NFLX", "DIS", "TMUS"],
    }
    results = []
    for symbol in groups.get(sector, []):
        if symbol == ticker.upper():
            continue
        p = fetch_snapshot(symbol)
        if p:
            results.append({"ticker": symbol, "company": p.get("longName"),
                            "trailing_pe": p.get("trailingPE"), "forward_pe": p.get("forwardPE"),
                            "price_to_book": p.get("priceToBook"),
                            "enterprise_to_ebitda": p.get("enterpriseToEbitda"),
                            "market_cap": p.get("marketCap")})
    return {"sector": info.get("sector"), "candidates": results,
            "note": "Candidate set only; direct comparability is not guaranteed."}

def run_dcf_model(fcf, current_price, market_cap, total_debt=0, cash=0,
                  growth_rate=0.08, discount_rate=0.10, terminal_growth=0.03, years=5):
    """Illustrative DCF scenario. Assumptions are explicit and not forecasts."""
    if not isinstance(fcf, (int, float)) or fcf <= 0:
        return None
    if not isinstance(current_price, (int, float)) or current_price <= 0:
        return None
    if not isinstance(market_cap, (int, float)) or market_cap <= 0:
        return None
    if discount_rate <= terminal_growth:
        return None
    shares = market_cap / current_price
    projections = [fcf * (1 + growth_rate) ** year for year in range(1, years + 1)]
    pv = sum(value / (1 + discount_rate) ** year for year, value in enumerate(projections, 1))
    terminal = projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    enterprise_value = pv + terminal / (1 + discount_rate) ** years
    equity_value = enterprise_value - (total_debt or 0) + (cash or 0)
    return {
        "scenario_intrinsic_value_per_share": equity_value / shares,
        "equity_value_scenario": equity_value,
        "implied_shares": shares,
        "projected_fcf": projections,
        "assumptions": {"years": years, "growth_rate": growth_rate,
                        "discount_rate": discount_rate, "terminal_growth": terminal_growth}
    }

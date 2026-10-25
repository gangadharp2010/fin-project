"""Financial statement and ratio tools backed by shared cached Yahoo Finance calls."""
from functools import lru_cache
from typing import Any
import math
import yfinance as yf

MISSING = "Cannot be confirmed from available information."

def _clean(value: Any):
    try:
        if value is None:
            return None
        if hasattr(value, "item"):
            value = value.item()
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return value
    except Exception:
        return None

def _frame_to_dict(frame):
    if frame is None or getattr(frame, "empty", True):
        return {}
    result = {}
    for period in frame.columns:
        result[str(period)] = {str(k): _clean(v) for k, v in frame[period].items()}
    return result

@lru_cache(maxsize=128)
def get_company_info(ticker: str) -> dict:
    try:
        raw = yf.Ticker(ticker.upper()).get_info() or {}
    except Exception:
        raw = {}
    keys = [
        "longName", "symbol", "sector", "industry", "country", "currency",
        "currentPrice", "regularMarketPrice", "marketCap", "enterpriseValue",
        "totalRevenue", "revenueGrowth", "grossMargins", "operatingMargins",
        "profitMargins", "returnOnEquity", "trailingPE", "forwardPE", "priceToBook",
        "enterpriseToEbitda", "totalCash", "totalDebt", "currentRatio", "quickRatio",
        "sharesOutstanding", "beta", "dividendYield", "freeCashflow", "operatingCashflow"
    ]
    return {k: _clean(raw.get(k)) for k in keys if raw.get(k) is not None}

@lru_cache(maxsize=128)
def _statement(ticker: str, kind: str) -> dict:
    try:
        stock = yf.Ticker(ticker.upper())
        frame = {"income": stock.income_stmt, "balance": stock.balance_sheet,
                 "cashflow": stock.cashflow}[kind]
        return _frame_to_dict(frame)
    except Exception:
        return {}

def get_income_statement(ticker: str) -> dict:
    return dict(_statement(ticker.upper(), "income"))

def get_balance_sheet(ticker: str) -> dict:
    return dict(_statement(ticker.upper(), "balance"))

def get_cash_flow_statement(ticker: str) -> dict:
    return dict(_statement(ticker.upper(), "cashflow"))

def _latest_line(statement, names):
    names = {n.lower() for n in names}
    for _, rows in statement.items():
        for name, value in rows.items():
            if name.lower() in names and value is not None:
                return value
    return None

def compute_key_ratios(ticker: str) -> dict:
    info = get_company_info(ticker)
    income = get_income_statement(ticker)
    balance = get_balance_sheet(ticker)
    cashflow = get_cash_flow_statement(ticker)
    revenue = info.get("totalRevenue") or _latest_line(income, ["Total Revenue", "Operating Revenue"])
    net_income = _latest_line(income, ["Net Income", "Net Income Common Stockholders"])
    op_cf = info.get("operatingCashflow") or _latest_line(
        cashflow, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
    capex = _latest_line(cashflow, ["Capital Expenditure", "Capital Expenditures"])
    fcf = info.get("freeCashflow")
    if fcf is None and op_cf is not None and capex is not None:
        fcf = op_cf + capex if capex < 0 else op_cf - capex
    debt = info.get("totalDebt") or _latest_line(balance, ["Total Debt", "Long Term Debt"])
    cash = info.get("totalCash") or _latest_line(
        balance, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])
    return {
        "revenue": _clean(revenue), "net_income": _clean(net_income),
        "operating_cash_flow": _clean(op_cf), "free_cash_flow": _clean(fcf),
        "total_debt": _clean(debt), "cash_and_equivalents": _clean(cash),
        "gross_margin": info.get("grossMargins"), "operating_margin": info.get("operatingMargins"),
        "net_margin": info.get("profitMargins"), "return_on_equity": info.get("returnOnEquity"),
        "current_ratio": info.get("currentRatio"), "quick_ratio": info.get("quickRatio"),
        "trailing_pe": info.get("trailingPE"), "forward_pe": info.get("forwardPE"),
        "price_to_book": info.get("priceToBook"), "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
        "market_cap": info.get("marketCap"), "enterprise_value": info.get("enterpriseValue"),
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "beta": info.get("beta"),
    }

def clear_cache():
    """Clear cached data when a fresh provider request is needed."""
    get_company_info.cache_clear()
    _statement.cache_clear()

"""Fetch a single compact snapshot per ticker and reuse it across agents."""
from __future__ import annotations
from dataclasses import dataclass
from functools import lru_cache
import os
import time
from typing import Any
import yfinance as yf

MISSING = "Cannot be confirmed from available information."

def _clean(v: Any):
    try:
        if v is None:
            return None
        if hasattr(v, "item"):
            v = v.item()
        if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
            return None
        return v
    except Exception:
        return None

def _frame_to_dict(frame, max_periods=4, max_rows=24):
    if frame is None or getattr(frame, "empty", True):
        return {}
    out = {}
    for period in list(frame.columns)[:max_periods]:
        rows = {}
        for item, value in list(frame[period].items())[:max_rows]:
            rows[str(item)] = _clean(value)
        out[str(period)] = rows
    return out

def _statement_line(statement, names):
    target = {n.lower() for n in names}
    for _, rows in statement.items():
        for name, value in rows.items():
            if name.lower() in target and value is not None:
                return value
    return None

def _fetch_snapshot_uncached(ticker: str) -> dict:
    # One Ticker object per snapshot; all agents receive this same result.
    stock = yf.Ticker(ticker)
    try:
        raw_info = stock.get_info() or {}
    except Exception as exc:
        raw_info = {}
        info_error = f"Company info unavailable: {type(exc).__name__}"
    else:
        info_error = None

    info_keys = [
        "longName", "symbol", "sector", "industry", "country", "currency",
        "currentPrice", "regularMarketPrice", "marketCap", "enterpriseValue",
        "totalRevenue", "revenueGrowth", "grossMargins", "operatingMargins",
        "profitMargins", "returnOnEquity", "trailingPE", "forwardPE", "priceToBook",
        "enterpriseToEbitda", "totalCash", "totalDebt", "currentRatio", "quickRatio",
        "sharesOutstanding", "beta", "dividendYield", "freeCashflow", "operatingCashflow"
    ]
    info = {k: _clean(raw_info.get(k)) for k in info_keys if raw_info.get(k) is not None}

    statements = {}
    for label, attr in [("income_statement", "income_stmt"),
                        ("balance_sheet", "balance_sheet"),
                        ("cash_flow_statement", "cashflow")]:
        try:
            statements[label] = _frame_to_dict(getattr(stock, attr))
        except Exception:
            statements[label] = {}

    try:
        raw_news = stock.news or []
    except Exception:
        raw_news = []
    news = []
    for item in raw_news[:10]:
        content = item.get("content", item)
        title = content.get("title")
        provider = content.get("provider", {})
        publisher = provider.get("displayName") if isinstance(provider, dict) else provider
        url = content.get("canonicalUrl", {})
        url = url.get("url") if isinstance(url, dict) else url
        if title:
            news.append({"title": title, "publisher": publisher,
                         "published": content.get("pubDate"), "url": url})

    income = statements["income_statement"]
    balance = statements["balance_sheet"]
    cashflow = statements["cash_flow_statement"]
    revenue = info.get("totalRevenue") or _statement_line(income, ["Total Revenue", "Operating Revenue"])
    net_income = _statement_line(income, ["Net Income", "Net Income Common Stockholders"])
    operating_cf = info.get("operatingCashflow") or _statement_line(
        cashflow, ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"])
    capex = _statement_line(cashflow, ["Capital Expenditure", "Capital Expenditures"])
    fcf = info.get("freeCashflow")
    if fcf is None and operating_cf is not None and capex is not None:
        fcf = operating_cf + capex if capex < 0 else operating_cf - capex
    debt = info.get("totalDebt") or _statement_line(balance, ["Total Debt", "Long Term Debt"])
    cash = info.get("totalCash") or _statement_line(
        balance, ["Cash And Cash Equivalents", "Cash Cash Equivalents And Short Term Investments"])

    ratios = {
        "revenue": _clean(revenue), "net_income": _clean(net_income),
        "operating_cash_flow": _clean(operating_cf), "free_cash_flow": _clean(fcf),
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
    return {"ticker": ticker, "company_info": info, "statements": statements,
            "key_ratios": ratios, "news": news, "data_source": "Yahoo Finance via yfinance",
            "data_warnings": [info_error] if info_error else []}

# Simple TTL cache: LRU bounds memory; expiration avoids indefinite stale results.
_CACHE = {}
_CACHE_MAX = 64

def fetch_snapshot(ticker: str, *, force_refresh: bool = False) -> dict:
    ticker = ticker.strip().upper()
    ttl = max(0, int(os.getenv("DATA_CACHE_TTL_SECONDS", "300")))
    now = time.monotonic()
    cached = _CACHE.get(ticker)
    if not force_refresh and cached and now - cached[0] < ttl:
        return cached[1]
    snapshot = _fetch_snapshot_uncached(ticker)
    _CACHE[ticker] = (now, snapshot)
    if len(_CACHE) > _CACHE_MAX:
        oldest = min(_CACHE, key=lambda k: _CACHE[k][0])
        _CACHE.pop(oldest, None)
    return snapshot

def clear_cache():
    _CACHE.clear()

def compact_statement_context(snapshot: dict) -> dict:
    """Only return a few useful rows/periods for prompts; preserve full snapshot for JSON output."""
    ratios = snapshot.get("key_ratios", {})
    wanted = {
        "income_statement": ["Total Revenue", "Operating Revenue", "Gross Profit", "Operating Income",
                             "Net Income", "Net Income Common Stockholders"],
        "balance_sheet": ["Total Assets", "Total Debt", "Long Term Debt", "Stockholders Equity",
                          "Cash And Cash Equivalents", "Current Assets", "Current Liabilities"],
        "cash_flow_statement": ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
                                "Cash Flow From Continuing Operating Activities"],
    }
    compact = {}
    for statement_name, row_names in wanted.items():
        source = snapshot.get("statements", {}).get(statement_name, {})
        compact[statement_name] = {}
        for period, rows in list(source.items())[:3]:
            compact[statement_name][period] = {
                name: value for name, value in rows.items()
                if name in row_names and value is not None
            }
    return {"ticker": snapshot.get("ticker"), "company_info": snapshot.get("company_info"),
            "key_ratios": ratios, "selected_statement_rows": compact,
            "recent_headlines": snapshot.get("news", [])[:8],
            "data_warnings": snapshot.get("data_warnings", [])}

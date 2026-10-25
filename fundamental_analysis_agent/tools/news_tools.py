"""Recent headline retrieval and sentiment-analysis helper."""
from functools import lru_cache
import yfinance as yf
from ..llm_client import ask_llm

@lru_cache(maxsize=128)
def search_recent_news(ticker: str) -> tuple:
    try:
        items = yf.Ticker(ticker.upper()).news or []
    except Exception:
        items = []
    out = []
    for item in items[:15]:
        content = item.get("content", item)
        title = content.get("title")
        provider = content.get("provider", {})
        publisher = provider.get("displayName") if isinstance(provider, dict) else provider
        url = content.get("canonicalUrl", {})
        url = url.get("url") if isinstance(url, dict) else url
        if title:
            out.append({"title": title, "publisher": publisher,
                        "published": content.get("pubDate"), "url": url})
    return tuple(out)

def analyze_sentiment(ticker: str) -> dict:
    headlines = list(search_recent_news(ticker))
    if not headlines:
        return {"headlines": [], "analysis": "Cannot be confirmed from available information."}
    import json
    analysis = ask_llm(
        "Classify headline tone as STRONGLY BULLISH, BULLISH, NEUTRAL, BEARISH, "
        "STRONGLY BEARISH or UNCONFIRMED. Use only supplied headlines; do not infer "
        "unreported facts. State uncertainty.",
        f"Ticker: {ticker}\nHeadlines:\n{json.dumps(headlines, default=str)}"
    )
    return {"headlines": headlines, "analysis": analysis}

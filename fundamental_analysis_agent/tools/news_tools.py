"""News tools consume the shared ticker snapshot; they do not make their own fetch."""
from ..llm_client import ask_llm

def search_recent_news(snapshot: dict) -> list:
    return list(snapshot.get("news", []))

def analyze_sentiment(snapshot: dict) -> dict:
    headlines = search_recent_news(snapshot)
    if not headlines:
        return {"headlines": [], "analysis": "Cannot be confirmed from available information."}
    # Headline-only prompt keeps token count small.
    titles = [{"title": h.get("title"), "publisher": h.get("publisher")} for h in headlines[:8]]
    import json
    analysis = ask_llm(
        "Classify sentiment as STRONGLY BULLISH, BULLISH, NEUTRAL, BEARISH, "
        "STRONGLY BEARISH, or UNCONFIRMED. Use only supplied headlines; do not infer "
        "unreported facts. Explain uncertainty.",
        f"Ticker: {snapshot['ticker']}\nHeadlines: {json.dumps(titles, ensure_ascii=False)}"
    )
    return {"headlines": headlines, "analysis": analysis}

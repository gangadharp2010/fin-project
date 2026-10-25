from ..tools.news_tools import analyze_sentiment, search_recent_news

class NewsAndSentimentAgent:
    name = "NewsAndSentimentAgent"

    def run(self, ticker):
        result = analyze_sentiment(ticker)
        return {"agent": self.name, **result, "headlines": result.get("headlines", list(search_recent_news(ticker)))}

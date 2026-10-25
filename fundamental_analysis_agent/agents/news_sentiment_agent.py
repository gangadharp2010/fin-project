from ..tools.news_tools import analyze_sentiment

class NewsAndSentimentAgent:
    name = "NewsAndSentimentAgent"

    def run(self, snapshot: dict) -> dict:
        return {"agent": self.name, **analyze_sentiment(snapshot)}

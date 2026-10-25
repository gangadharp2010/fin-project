
from concurrent.futures import ThreadPoolExecutor

from fundamental_analysis_agent.tools.financial_tools import fetch_snapshot

from .financial_data_agent import FinancialDataAgent
from .news_sentiment_agent import NewsAndSentimentAgent
from .risk_agent import RiskAgent
from .valuation_agent import ValuationAgent
from .report_writer_agent import ReportWriterAgent


class OrchestratorAgent:
    """Coordinate the fundamental analysis agents."""

    def __init__(self):
        self.financial = FinancialDataAgent()
        self.news = NewsAndSentimentAgent()
        self.risk = RiskAgent()
        self.valuation = ValuationAgent()
        self.writer = ReportWriterAgent()

    def run(self, ticker: str, *, force_refresh: bool = False) -> dict:
        ticker = ticker.strip().upper()

        # Fetch financial data once.
        snapshot = fetch_snapshot(
            ticker,
            force_refresh=force_refresh,
        )

        # Phase 1: Run independent analyses in parallel.
        with ThreadPoolExecutor(max_workers=3) as pool:
            f_financial = pool.submit(
                self.financial.run, snapshot
            )
            f_news = pool.submit(
                self.news.run, snapshot
            )
            f_risk = pool.submit(
                self.risk.run, snapshot
            )

            financial = f_financial.result()
            news = f_news.result()
            risk = f_risk.result()

        # Phase 2: Run valuation.
        valuation = self.valuation.run(
            ticker, financial, snapshot
        )

        # Phase 3: Generate the final report.
        final_report = self.writer.run(
            ticker, financial, news, risk, valuation
        )

        return {
            "ticker": ticker,
            "financial_report": financial,
            "news_report": news,
            "risk_report": risk,
            "valuation_report": valuation,
            "final_report": final_report,
            "raw_snapshot": snapshot,
        }

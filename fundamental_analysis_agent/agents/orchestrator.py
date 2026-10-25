from concurrent.futures import ThreadPoolExecutor
from .financial_data_agent import FinancialDataAgent
from .news_sentiment_agent import NewsAndSentimentAgent
from .risk_agent import RiskAgent
from .valuation_agent import ValuationAgent
from .report_writer_agent import ReportWriterAgent

class OrchestratorAgent:
    """Phase 1: three agents in parallel; Phase 2: valuation; Phase 3: final brief."""
    def __init__(self):
        self.financial = FinancialDataAgent()
        self.news = NewsAndSentimentAgent()
        self.risk = RiskAgent()
        self.valuation = ValuationAgent()
        self.writer = ReportWriterAgent()

    def run(self, ticker):
        ticker = ticker.strip().upper()
        with ThreadPoolExecutor(max_workers=3, thread_name_prefix="research-agent") as pool:
            f_financial = pool.submit(self.financial.run, ticker)
            f_news = pool.submit(self.news.run, ticker)
            f_risk = pool.submit(self.risk.run, ticker)
            financial = f_financial.result()
            news = f_news.result()
            risk = f_risk.result()

        valuation = self.valuation.run(ticker, financial)
        final_report = self.writer.run(ticker, financial, news, risk, valuation)
        return {
            "ticker": ticker,
            "workflow": [
                "FinancialDataAgent + NewsAndSentimentAgent + RiskAgent (parallel)",
                "ValuationAgent (after financial data)",
                "ReportWriterAgent (synthesizes all four specialist reports)"
            ],
            "financial_report": financial,
            "news_report": news,
            "risk_report": risk,
            "valuation_report": valuation,
            "final_report": final_report
        }

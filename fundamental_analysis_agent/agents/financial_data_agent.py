import json
from ..tools import financial_tools as ft
from ..llm_client import ask_llm

class FinancialDataAgent:
    name = "FinancialDataAgent"

    def run(self, ticker):
        company = ft.get_company_info(ticker)
        statements = {
            "income_statement": ft.get_income_statement(ticker),
            "balance_sheet": ft.get_balance_sheet(ticker),
            "cash_flow_statement": ft.get_cash_flow_statement(ticker),
        }
        ratios = ft.compute_key_ratios(ticker)
        analysis = ask_llm(
            "Act as a junior financial analyst. Summarize reported revenue, profitability, "
            "cash flow, margins and ROE. Do not infer trends from a single period.",
            f"Ticker: {ticker}\nCompany: {json.dumps(company, default=str)}\n"
            f"Statements: {json.dumps(statements, default=str)}\nRatios: {json.dumps(ratios, default=str)}"
        )
        return {"agent": self.name, "company_info": company, "statements": statements,
                "key_ratios": ratios, "analysis": analysis}

from ..llm_client import ask_llm
from ..tools.financial_tools import compact_statement_context

class FinancialDataAgent:
    name = "FinancialDataAgent"

    def run(self, snapshot: dict) -> dict:
        print(      "DEBUG FinancialDataAgent:",        type(snapshot).__name__,    )
        
        if not isinstance(snapshot, dict):
            raise TypeError(
                f"Expected snapshot dict, got {type(snapshot).__name__}. "
                "Check orchestrator.py."
            )

        compact = compact_statement_context(snapshot)

        analysis = ask_llm(
            "Summarize financial health, revenue, profitability, "
            "cash flow, margins and ROE. Use only supplied data. "
            "Never invent missing financial values.",
            str(compact),
        )

        return {
            "agent": self.name,
            "key_ratios": snapshot.get("key_ratios", {}),
            "analysis": analysis,
        }

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone
from .agents.orchestrator import OrchestratorAgent

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m fundamental_analysis_agent.main TICKER")
        raise SystemExit(2)
    ticker = sys.argv[1].strip().upper()
    if not re.fullmatch(r"[A-Z0-9.^=-]{1,20}", ticker):
        raise SystemExit("Invalid ticker format.")
    print(f"Starting fundamental analysis for {ticker}...")
    result = OrchestratorAgent().run(ticker)
    reports = Path("reports")
    reports.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    md = reports / f"{ticker}_fundamental_report.md"
    js = reports / f"{ticker}_fundamental_report.json"
    md.write_text(f"# Fundamental Analysis Brief — {ticker}\n\nGenerated: {stamp}\n\n"
                  + result["final_report"] + "\n", encoding="utf-8")
    js.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print("\n" + result["final_report"])
    print(f"\nSaved Markdown: {md.resolve()}\nSaved JSON: {js.resolve()}")

if __name__ == "__main__":
    main()

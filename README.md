# Fundamental Analysis Agent

Project layout follows the requested `agents/` and `tools/` structure.

## Setup (Windows PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Set `OPENAI_API_KEY` and optionally `OPENAI_MODEL` in `.env`, then run:
```powershell
python -m fundamental_analysis_agent.main AAPL
```

Reports are saved under `reports/`.

Yahoo Finance data may be incomplete or delayed. DCF outputs are assumption-driven scenarios, not forecasts or personalized financial advice. Missing facts must be reported as `Cannot be confirmed from available information.`

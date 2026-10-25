import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
RULES = """Use only supplied data. Never invent financial values, dates, news, peer metrics,
or citations. For missing facts, write exactly 'Cannot be confirmed from available information.'
Separate facts from assumptions. Educational analysis only; not personalized financial advice."""

def ask_llm(task: str, payload: str) -> str:
    if not os.getenv("OPENAI_API_KEY"):
        return "AI interpretation unavailable: OPENAI_API_KEY is not configured."
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        input=[{"role": "system", "content": RULES + "\n" + task},
               {"role": "user", "content": payload}]
    )
    return response.output_text
